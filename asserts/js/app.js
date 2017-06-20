angular.module('authApp', ['ngResource', 'ngRoute', 'ui.bootstrap', 'angular-loading-bar', 'chart.js']).
    config(['$httpProvider', function($httpProvider){
        // django and angular both support csrf tokens. This tells
        // angular which cookie to add to what header.
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }]).
    config(function($routeProvider){
        $routeProvider.when('/profile',
        {
            templateUrl:'static/views/profile.html',
            controller:'profileController'
        }).when('/index',
        {
            templateUrl:'static/views/index.html',
            controller:'indexController'
        }).otherwise({redirectTo: "/index"});
    }).
    config(['ChartJsProvider', function (ChartJsProvider) {
        // Configure all charts
        ChartJsProvider.setOptions({
            chartColors: ['#FF5252', '#FF8A80'],
            responsive: true
        });
        // Configure all line charts
        ChartJsProvider.setOptions('line', {
            showLines: true
        });
    }]).
    factory('api', function($resource){
        function add_auth_header(data, headersGetter){
            // as per HTTP authentication spec [1], credentials must be
            // encoded in base64. Lets use window.btoa [2]
            var headers = headersGetter();
            headers['Authorization'] = ('Basic ' + btoa(data.username +
                                        ':' + data.password));
        }
        // defining the endpoints. Note we escape url trailing dashes: Angular
        // strips unescaped trailing slashes. Problem as Django redirects urls
        // not ending in slashes to url that ends in slash for SEO reasons, unless
        // we tell Django not to [3]. This is a problem as the POST data cannot
        // be sent with the redirect. So we want Angular to not strip the slashes!
        return {
            auth: $resource('/api/auth\\/', {}, {
                login: {method: 'POST', transformRequest: add_auth_header},
                logout: {method: 'DELETE'}
            }),
            users: $resource('/api/users\\/', {}, {
                create: {method: 'POST'}
            })
        };
    }).
    controller('authController', function($scope, api, $location) {
        // Angular does not detect auto-fill or auto-complete. If the browser
        // autofills "username", Angular will be unaware of this and think
        // the $scope.username is blank. To workaround this we use the
        // autofill-event polyfill [4][5]
        //$('#id_auth_form input').checkAndTriggerAutoFillEvent();
 
        $scope.getCredentials = function(){
            return {username: $scope.username, password: $scope.password, email: $scope.email};
        };
 
        $scope.login = function(){
            api.auth.login($scope.getCredentials()).
                $promise.
                    then(function(data){
                        // on good username and password
                        $scope.user = data;
                        $scope.userData = data;
                        $location.path('/profile');
                    }).
                    catch(function(data){
                        // on incorrect username and password
                        alert(data.data.detail);
                    });
        };
 
        $scope.logout = function(){
            api.auth.logout(function(){
                $scope.user = undefined;
                $location.path('/index');
            });
        };
        $scope.register = function($event){
            // prevent login form from firing
            $event.preventDefault();
            // create user and immediatly login on success
            api.users.create($scope.getCredentials()).
                $promise.then($scope.login)
            };
    }).controller('profileController', function($scope, api, $location, $http, $filter) {
        $scope.receipts = [];
        $scope.currentPage = 1;
        $scope.maxSize = 5;
        $scope.totalItems = 0;
        $scope.dateOptions = {
            formatYear: 'yy',
            startingDay: 1
        };

        $scope.formats = 'dd-MMMM-yyyy';
        $scope.popupStart = {opened: false}
        $scope.popupEnd = {opened: false}

        $scope.$watch('user', function(newValue, oldValue) {
            $scope.getProfile();
        });

        $scope.pageChanged = function() {
            $scope.page = 1;
            $scope.getProfile();
        };

        $scope.getProfile = function () {
            $scope.receipts = [];
            var search = '';
            var user = undefined;
            search += "page_num=" + $scope.currentPage;
            if ($scope.dateStart) search += "&date_start=" + $scope.dateStart;
            if ($scope.dateEnd) search += "&date_end=" + $scope.dateEnd;
            if ($scope.name) search += "&name=" + $scope.name;
            if ($scope.storeName) search += "&user=" + $scope.storeName;

            $http.get("api/profiles?" + search).then(function (data) {
                console.log('success');
                if (data && data.data && data.data.results[0] && data.data.results[0].receipts)
                    $scope.totalItems = data.data.results[0].rec_count;
                    $scope.receipts = data.data.results[0].receipts;
                    $scope.totalSum = data.data.results[0].rec_summ.total_sum__sum;
                    $scope.excludeSum = data.data.results[0].exclude_summ.items__sum__sum;
                    $scope.$parent.userData = data.data.results[0].user;
                    $scope.excludeArr = data.data.results[0].exclude_array;
                    $scope.recArr = data.data.results[0].rec_array;

                    $scope.labels = [];
                    $scope.series = ['Сэкономленное', 'Потраченное'];

                    $scope.itemsExclude = []
                    for (ex in $scope.recArr) {
                        $scope.itemsExclude[ex] = 0;
                        for (i in $scope.excludeArr) {
                            if ($scope.recArr[ex].id == $scope.excludeArr[i].id) {
                                $scope.itemsExclude[ex] = $scope.excludeArr[i].items_sum / 100;
                            }
                        }
                        $scope.labels.push($scope.recArr[ex].date_time);
                        $scope.recArr[ex] = $scope.recArr[ex].total_sum / 100;
                        
                    }

                    $scope.data = [
                        $scope.itemsExclude,
                        $scope.recArr
                    ];

            }, function () {
                console.log('error');
            });
        }

        $scope.openStart = function () {
            $scope.popupStart.opened = true
        }

        $scope.openEnd = function () {
            $scope.popupEnd.opened = true
        }

        $scope.applyFilters = function () {
            if ($scope.dateStart) $scope.dateStart = $filter('date')($scope.dateStart, "yyyy-MM-dd");
            if ($scope.dateEnd) $scope.dateEnd = $filter('date')($scope.dateEnd, "yyyy-MM-dd");
            $scope.getProfile();
        }

        $scope.resetFilters = function () {
            $scope.dateStart = null;
            $scope.dateEnd = null;
            $scope.name = null;
            $scope.storeName = null;
            $scope.getProfile();
        }

        $scope.deleteRec = function (receipt) {
            $http.delete("api/receipts/" + receipt.id).then(function (data) {
                console.log('success');
                $scope.getProfile();
            }, function () {
                console.log('error');
            });
        }

        $scope.uploadFile = function(files) {
            var fd = new FormData();
            //Take the first selected file
            fd.append("file", files[0]);

            $http.post("api/upload/", fd, {
                withCredentials: true,
                headers: {'Content-Type': undefined },
                transformRequest: angular.identity
            }).success(function () {
                console.log('success');
                $scope.getProfile();
            }).error(function () {
                console.log('error');
            });
        };

        $scope.exclude = function (item) {
            $http.post("api/items/" + item.id + "/", item).then(function (data) {
                console.log('success');
                $scope.getProfile();
            }, function () {
                console.log('error');
            });
        }
        //$scope.getProfile();
        //$scope.labels = ["January", "February", "March", "April", "May", "June", "July"];
        //$scope.series = ['Series A', 'Series B'];

        $scope.onClick = function (points, evt) {
            console.log(points, evt);
        };

        $scope.datasetOverride = [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }];
        $scope.options = {
            scales: {
                yAxes: [
                    {
                      id: 'y-axis-1',
                      type: 'linear',
                      display: true,
                      position: 'left'
                    },
                    {
                      id: 'y-axis-2',
                      type: 'linear',
                      display: true,
                      position: 'right'
                    }
                ]
            }
        };

        tour = new Shepherd.Tour({
          defaults: {
            classes: 'shepherd-theme-default'
          }
        });

        tour.addStep('upload', {
          title: 'Пример использования',
          text: 'Нажмите на кнопку для загрузки чеков в приложение. Этот файл вам надо получить через приложение "Проверка чеков", которое можно скачать из AppStore или GooglePlay.',
          attachTo: '.upload bottom',
          buttons: [{
            text: 'Далее',
            action: tour.next
          }]
        });

        tour.addStep('list', {
          title: 'Пример использования',
          text: 'Здесь вы можете найти список ваших загруженных чеков. Обратите внимание, что их можно раскрыть для просмотра информации о товарах и удалить.',
          attachTo: '.receipts-list left',
          buttons: [{
            text: 'Далее',
            action: tour.next
          }]
        });

        tour.addStep('filter-list', {
          title: 'Пример использования',
          text: 'С помощью фильтров вы можете найти те чеки, которые хотели бы отобразить.',
          attachTo: '.filter-list right',
          buttons: [{
            text: 'Далее',
            action: tour.next
          }]
        });

        tour.addStep('sum-list', {
          title: 'Пример использования',
          text: 'Здесь отобразятся суммарные данные о ваших покупках. Обратите внимание, что эти данные относятся ко всем отфильтрованным страницам',
          attachTo: '.sum-list bottom',
          buttons: [{
            text: 'Далее',
            action: tour.next
          }]
        });

        tour.addStep('visual', {
          title: 'Пример использования',
          text: 'Визуальная оценка ваших затрат. Обратите внимание, что эти данные относятся ко всем отфильтрованным страницам',
          attachTo: '.visual top',
          buttons: [{
            text: 'Далее',
            action: tour.next
          }]
        });

        $scope.showHint = function () {
            tour.start();
        }        

    }).controller('indexController', function($scope, api, $location, $http, $filter) {
        var backgroundResize;
        backgroundResize = function() {
          var contH, contW, imgH, imgW, path, ratio, windowH;
          windowH = $(window).height();
          path = $('.background');
          contW = path.width();
          contH = path.height();
          imgW = path.attr('data-img-width');
          imgH = path.attr('data-img-height');
          ratio = imgW / imgH;
          imgH = contH;
          imgW = imgH * ratio;
          if (contW > imgW) {
            imgW = contW;
            imgH = imgW / ratio;
          }
          path.data('resized-imgW', imgW);
          path.data('resized-imgH', imgH);
          return path.css('background-size', imgW + 'px ' + imgH + 'px');
        };
        $(window).resize(backgroundResize);
        $(window).focus(backgroundResize);
        return backgroundResize();
        
   })
