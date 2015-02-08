angular.module('reinvestApp.controllers', []).controller('MapController', function($scope, uiGmapGoogleMapApi, dataService) {
	$scope.landData = false;

	dataService.getLandDataForMap().then(function(data) {
		$scope.landData = data;
	}, function() {
		// error could not retrieve data
	});


	uiGmapGoogleMapApi.then(function(maps) {
		$scope.map = {
			center: {
				latitude: 47.614848,
				longitude: -122.3359059
			},
			zoom: 15
		};

	});

})


.controller('PlotDetailsController', function($scope) {

})


.controller('PortfolioController', function($scope) {
	
});
