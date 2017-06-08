angular.module('authApp', ['ngResource', 'ngRoute', 'ui.grid', 'ui.grid.selection', 'ui.bootstrap', 'ngAnimate']).
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
    }).controller('profileController', function($scope, api, $location, $http, uiGridConstants) {
        $scope.receipts = [];

        $scope.$watch('user', function(newValue, oldValue) {
            $scope.getProfile();
        });

        $scope.getProfile = function () {
            $scope.receipts = [];
            $http.get("api/profiles").then(function (data) {
                console.log('success');
                if (data && data.data && data.data.results[0] && data.data.results[0].receipts)
                    $scope.gridOptions.data = data.data.results[0].receipts;
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

        $scope.getProfile();

        $scope.gridOptions = {
            enableFiltering: true,
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
        },
        columnDefs: [
            {
                field: 'date_time',
                displayName: 'Date Time',
                enableFiltering: true,
                enableCellEdit: false,
                filterHeaderTemplate: '<div class="ui-grid-filter-container row"><div ng-repeat="colFilter in col.filters" class="col-md-6 col-md-offset-0 col-sm-6 col-sm-offset-0 col-xs-6 col-xs-offset-0"><div custom-grid-date-filter-header></div></div></div>',
                filters: [
                    {
                        name: 'From',
                        condition: uiGridConstants.filter.GREATER_THAN_OR_EQUAL
                    },
                    {
                        name: 'To',
                        condition: uiGridConstants.filter.LESS_THAN_OR_EQUAL
                    }
                ],
                cellFilter: 'date:"yyyy-M-dTHH:mm:ssZ"',
                width: '40%'
            },
            {
                field: 'user',
                displayName: 'Store',
                enableCellEdit: false,
                enableFiltering: false
            },
            {
                field: 'total_sum',
                displayName: 'Sum',
                enableCellEdit: false,
                enableFiltering: false
            }
        ]
    };

})

.controller('gridDatePickerFilterCtrl', ['$scope', '$timeout', '$uibModal', 'uiGridConstants', function( $scope, $timeout, $uibModal, uiGridConstants) {

    $timeout(function() {
        console.log($scope.col); 
        var field = $scope.col.colDef.name;

        var allDates = _.map($scope.col.grid.appScope.gridOptions.data, function(datum) {
            return datum[field];
        });
            
        var minDate = _.min(allDates);
        var maxDate = _.max(allDates);

        $scope.openDatePicker = function(filter) {
            
            var modalInstance = $uibModal.open({
                templateUrl: 'custom-date-filter.html',
                controller: 'customGridDateFilterModalCtrl as custom',
                size: 'md',
                windowClass: 'custom-date-filter-modal',
                resolve: {
                    filterName: [function() {
                        return filter.name;
                    }],
                    minDate: [function() {
                        return new Date(minDate);
                    }],
                    maxDate: [function() {
                        return new Date(maxDate);
                    }],
                }
            });
    
            modalInstance.result.then(function(selectedDate) {
                
                console.log('date', selectedDate);
                $scope.colFilter.listTerm = [];
                
                console.log(typeof selectedDate);
                console.log(selectedDate instanceof Date);
                
                $scope.colFilter.term = selectedDate;
            });
        };
            
    });
    

}])
.controller('customGridDateFilterModalCtrl', ['$scope', '$rootScope', '$log', '$uibModalInstance', 'filterName', 'minDate', 'maxDate', function($scope, $rootScope, $log, $uibModalInstance, filterName, minDate, maxDate) {
    
        var ctrl = this;

        console.log('filter name', filterName);
        console.log('min date', minDate, 'max date', maxDate);
        
        ctrl.title = 'Select Dates ' + filterName + '...';
        ctrl.minDate = minDate;
        ctrl.maxDate = maxDate;
        ctrl.customDateFilterForm;
    
        ctrl.filterDate = (filterName.indexOf('From') !== -1) ? angular.copy(ctrl.minDate) : angular.copy(ctrl.maxDate);
        
        function setDateToStartOfDay(date) {
            return new Date(date.getFullYear(), date.getMonth(), date.getDate());
        }

        function setDateToEndOfDay(date) {
            return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59);
        }

        ctrl.filterDateChanged = function () {
            ctrl.filterDate = (filterName.indexOf('From') !== -1) ? setDateToStartOfDay(ctrl.filterDate) : setDateToEndOfDay(ctrl.filterDate);
            $log.log('new filter date', ctrl.filterDate);
        };
        
        ctrl.setFilterDate = function(date) {
            $uibModalInstance.close(date);
        };

        ctrl.cancelDateFilter = function() {
            $uibModalInstance.dismiss();
        };
    
}])

.directive('customGridDateFilterHeader', function() {
    return {
        template: '<button class="btn btn-default date-time-filter-buttons" style="width:90%;padding:inherit;" ng-click="openDatePicker(colFilter)">{{ colFilter.name }}</button><div role="button" class="ui-grid-filter-button-select cancel-custom-date-range-filter-button ng-scope" ng-click="removeFilter(colFilter, $index)" ng-if="!colFilter.disableCancelFilterButton" ng-disabled="colFilter.term === undefined || colFilter.term === null || colFilter.term === \'\'" ng-show="colFilter.term !== undefined &amp;&amp; colFilter.term != null" tabindex="0" aria-hidden="false" aria-disabled="false" style=""><i class="ui-grid-icon-cancel cancel-custom-date-range-filter" ui-grid-one-bind-aria-label="aria.removeFilter" aria-label="Remove Filter">&nbsp;</i></div>',
        controller: 'gridDatePickerFilterCtrl'
    };
})
;