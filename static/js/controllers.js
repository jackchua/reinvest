angular.module('reinvestApp.controllers', []).controller('MapController', function($scope, uiGmapGoogleMapApi, dataService, $rootScope, $timeout) {
	$rootScope.onMarkerClicked = onMarkerClicked;


	$scope.updateFloors = function() {
		dataService.getCostsAndROIS($rootScope.currentMarkerProperty["Price"], $rootScope.currentMarkerProperty["Neighborhood"], $rootScope.currentMarkerProperty["floors"], $rootScope.currentMarkerProperty["lotSizeSqFt"]).then(function(data) {
			angular.extend($rootScope.currentMarkerProperty, data);
		}, function() {
			// error could not retrieve construction and ROI data
		});
	}
	
	$scope.showAddButton = function( propertyID ){
	    if( $rootScope.portfolio.indexOf(propertyID) > -1) {
	       return false;
	    }

	    return true;
	}

	
	$scope.addToPortfolio = function( propertyID ){
	    $rootScope.portfolio.push(propertyID);
	}

	
	$scope.removeFromPortfolio = function( propertyID ){
		var i = $rootScope.portfolio.indexOf(propertyID);
		$rootScope.portfolio = $rootScope.portfolio.splice(i, 1);
	}

	var onMarkerClicked = function(marker) {
			$rootScope.foldOpen = true;
			marker.icon = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|2375C2";

			$rootScope.$apply();

			$rootScope.currentMarkerID = marker.id;
			$rootScope.currentMarkerProperty = $rootScope.landData[marker.id];
			
			var hasLandDataForFold = $rootScope.currentMarkerProperty["lotSizeSqFt"];

			if (!hasLandDataForFold) {
				dataService.getLandDataForFold($rootScope.currentMarkerProperty["Price"], $rootScope.currentMarkerProperty["Address"], $rootScope.currentMarkerProperty["City"] + ", " + $rootScope.currentMarkerProperty["State"]).then(function(data) {
					$rootScope.currentMarkerProperty.lotSizeSqFt = data.lotSizeSqFt;
					$rootScope.currentMarkerProperty.floors = 5;

					dataService.getCostsAndROIS($rootScope.currentMarkerProperty["Price"], $rootScope.currentMarkerProperty["Neighborhood"], $rootScope.currentMarkerProperty["floors"], $rootScope.currentMarkerProperty["lotSizeSqFt"]).then(function(data) {
						angular.extend($rootScope.currentMarkerProperty, data);
						$scope.missingData = false;
					}, function() {
						$scope.missingData = true;
					});

				}, function() {
					// error could not retrieve lot square size data (map fold data)
				});
			}

			$scope.currentProperty = $rootScope.landData[marker.id];
			$scope.missingData = ( $rootScope.currentMarkerProperty.annualizedReturns === undefined ) ? true : false;

		};


	var createMarker = function(index, currentLandPlot) {
			var latitude = currentLandPlot["Latitude"] / 1000000,
				longitude = currentLandPlot["Longitude"] / 1000000;
			return {
				latitude: latitude,
				longitude: longitude,
				icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|EE3626",
				id: index
			};
		};

	var loadMarkers = function() {
			var markers = [],
				currentLandPlot;

			for (var i = 0; i < $rootScope.landData.length; i++) {
				currentLandPlot = $rootScope.landData[i];
				markers.push(createMarker(i, currentLandPlot))
			}
			$rootScope.markers = markers;

			_.each($rootScope.markers, function(marker) {
				marker.onClicked = function() {
					onMarkerClicked(marker);
				};
			});
		}


	if ($rootScope.landData.length === 0) {
		dataService.getLandDataForMap().then(function(data) {
			$rootScope.landData = data;

			loadMarkers();
		}, function() {
			// error could not retrieve available land plot data
		});
	}


}).controller('PortfolioController', function($scope) {

});
