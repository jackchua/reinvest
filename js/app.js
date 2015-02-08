var app = angular.module('reinvestApp', ['reinvestApp.controllers', 'ui.router', 'uiGmapgoogle-maps'])

.constant('API_SOURCE', (function() {
	var DOMAIN = 'http://54.190.42.247:5000';
	var CALLBACK = "?callback=JSON_CALLBACK"
	return {
		DATA_FOR_MAP: DOMAIN + '/get_land_data_for_map' + CALLBACK,
		DATA_FOR_FOLD: DOMAIN + '/get_land_data_for_fold' + CALLBACK,
		DATA_COSTS_ROIS : DOMAIN + '/compute_construction_cost_and_rois' + CALLBACK
	}
})())

.config(['$stateProvider', '$locationProvider', function($stateProvider, $locationProvider) {
	$stateProvider.state('homeView', {
		url: '/home',
		templateUrl: 'partials/home.html',
		data : { pageTitle: "ReInvest - Build a custom real estate investment" }
	});
	$stateProvider.state('mapView', {
		url: '/map',
		templateUrl: 'partials/map.html',
		controller: 'MapController',
		data : { pageTitle: "Search property listings - ReInvest" }
	});
	$stateProvider.state('plotDetails', {
		url: '/plot/:id',
		templateUrl: 'partials/plot.html',
		controller: 'PlotDetailsController',
		data : { pageTitle: "Property details - ReInvest" }
	});
	$stateProvider.state('portfolioView', {
		url: '/portfolio',
		templateUrl: 'partials/portfolio.html',
		controller: 'PortfolioController',
		data : { pageTitle: "My Portfolio - ReInvest" }
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
			return $http.jsonp(API_SOURCE.DATA_FOR_MAP).then(function(response) {
				return response.data;
			});
		},
		getLandDataForFold: function(price, address, citystatezip) {
			return $http.jsonp(API_SOURCE.DATA_FOR_FOLD + "&price=" + encodeURIComponent(price) + "&address=" + encodeURIComponent(address)  + "&citystatezip=" + encodeURIComponent(citystatezip)  ).then(function(response) {
				return response.data;
			});
		},		
		getCostsAndROIS: function(price, region, floors, lotSizeSqFt) {
			return $http.jsonp(API_SOURCE.DATA_COSTS_ROIS + "&price=" + encodeURIComponent(price) + "&region=" + encodeURIComponent(region)  + "&floors=" + encodeURIComponent(floors)  + "&lotSizeSqFt=" + encodeURIComponent(lotSizeSqFt)  ).then(function(response) {
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
	$rootScope.landData = [];
	
	$rootScope.map = {
		center: {
			latitude: 47.614848,
			longitude: -122.3359059
		},
		zoom: 15,
		bounds: {}
	};
	$rootScope.markers = [];
	$rootScope.$on("$routeChangeSuccess", function(currentRoute, previousRoute){
	    $rootScope.title = $state.current.title;
	  });
}]);
