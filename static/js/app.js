var app = angular.module('reinvestApp', ['reinvestApp.controllers', 'ui.router', 'uiGmapgoogle-maps'])

.constant('API_SOURCE', (function() {
	var DOMAIN = 'http://54.190.42.247:5000';
	return {
		LAND_DATA: DOMAIN + '/get_land_data_for_map'
	}
})())

.config(['$stateProvider', '$locationProvider', function($stateProvider, $locationProvider) {
	$stateProvider.state('homeView', {
		url: '/home',
		templateUrl: 'partials/home.html'
	});
	$stateProvider.state('mapView', {
		url: '/map',
		templateUrl: 'partials/map.html',
		controller: 'MapController'
	});
	$stateProvider.state('plotDetails', {
		url: '/plot/:id',
		templateUrl: 'partials/plot.html',
		controller: 'PlotDetailsController'
	});
	$stateProvider.state('portfolioView', {
		url: '/portfolio',
		templateUrl: 'partials/portfolio.html',
		controller: 'PortfolioController'
	});	
	// $locationProvider.html5Mode(true);
}])

.config(function(uiGmapGoogleMapApiProvider) {
	uiGmapGoogleMapApiProvider.configure({
		key: 'AIzaSyA0J3TS53d3V3ytQkhWnSlPuW_znbRZPl0',
		v: '3.17'
	});
})

.factory('dataService', function($http, API_SOURCE) {
	return {
		getLandDataForMap: function() {
			return $http.jsonp(API_SOURCE.LAND_DATA).then(function(response) {
				return response.data;
			});
		}
	}
})

.run(['$rootScope', '$state', '$stateParams', function($rootScope, $state, $stateParams) {
	$state.go('homeView');
	$rootScope.$state = $state;
	$rootScope.$stateParams = $stateParams;
	$rootScope.portfolio = [];
}]);
