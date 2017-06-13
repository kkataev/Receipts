angular.module('authApp', ['ngResource', 'ngRoute', 'ui.bootstrap', 'ngAnimate']).
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
        }).otherwise({redirectTo: "/"});
    }).
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
        $('#id_auth_form input').checkAndTriggerAutoFillEvent();
 
        $scope.getCredentials = function(){
            return {username: $scope.username, password: $scope.password};
        };
 
        $scope.login = function(){
            api.auth.login($scope.getCredentials()).
                $promise.
                    then(function(data){
                        // on good username and password
                        $scope.user = data.username;
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
            });
        };
        $scope.register = function($event){
            // prevent login form from firing
            $event.preventDefault();
            // create user and immediatly login on success
            api.users.create($scope.getCredentials()).
                $promise.then($scope.login)
            };
    }).controller('profileController', function($scope, api, $location, $http) {
        $scope.receipts = [];
        $scope.currentPage = 1;
        $scope.maxSize = 5;
        $scope.totalItems = 0;

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

        //$scope.getProfile();
    })
