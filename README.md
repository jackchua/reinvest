# ReInvest

This application was developed on February 8th, 2015 for the [Hack Housing](https://hack-housing.hackpad.com/) Hackathon.

Our app is live at http://jackchua.github.io/reinvest.

## Challenge and Approach

We decided to take a top-down approach in solving the lack of available housing in Seattle.

ReInvest provides a research platform for development projects that make use of empty land. We use time series forecasting methods (Holt-Winters, ARIMA) to arrive at forecasts for rental price per square foot for neighborhoods in the Seattle area. Due to time constraints and lack of high resolution data, we do not forecast and only make reasonable assumptions regarding cap rate, square foot utilization, and construction costs. With all of the above, we can arrive at 1, 5 and 10 year annualized ROI (return on investments) for all available land in Seattle showcased on Zillow.

It is our hope that people thinking about alternative investments might develop in empty, unused lots in underdeveloped areas.

## Team Members

Our team is comprised of:

- [@jackchua](https://sites.google.com/site/jackhschua/)
- [@xiaokunx](http://github.com/xiaokunx)
- [@cfan](http://github.com/cfan)

## Technologies, APIs, and Datasets Utilized

We made use of:

- Python
- R
- Flask
- MySQL RDS
- Angular.js

Datasets

- Mined Zillow.com map data for available land
- ZWS API (Deep Search)
- Zillow rentals data per square foot for Seattle
- Zillow ZHVI data

## Contributing

Our code is licensed under the [MIT License](LICENSE.md). Pull requests will be accepted to this repo, pending review and approval.
