require(ggplot2)
require(zoo)
require(dplyr)
setwd('data')

ZRIfile = 'Seattle_Neighborhood_Median_Rental_Price_Per_Sqft_All_Homes.csv'

toDate = function(char_vec) {
  date_vec = sapply(strsplit(char_vec, " "), function(x) x[1])
  return(as.Date(date_vec, "%m/%d/%Y"))
}

toTS = function(df, Region) {
  subdf = subset(df, Region.Name==Region, 'Value')
  return(ts(value_vec, start=c(2010,2), end=c(2014,11), frequency=12))
}

imputeTS = function(in_ts,template) {
  in_ts[is.na(in_ts)] = template[is.na(in_ts)]
  return(in_ts)
}

forecastTS= function(in_ts, nmonth) {
  # use Holter-Winters to fit the observed ts, and forecast the next 12 month
  hw = HoltWinters(in_ts)
  forecast = predict(hw, n.ahead = nmonth, prediction.interval = T, level = 0.95)
  df = data.frame(date=as.Date(time(forecast)), Value=as.data.frame(forecast)$fit)
  return(df)
}

# function to generate forecast dataframe
gen_forecastDF = function(df,nmonth_forecast) {

  # container df for forecasting
  forecast_df = data.frame()

  df$date = toDate(as.character(df$Month))
  df$Month= NULL
  df_copy = df
  # no data available for 2010-02-01
  df = subset(df, date>=as.Date('2010-04-01'))

  # compute a global (region-wide) mean time series for imputation at finer grain
  state_ts = summarise(group_by(df, date), Value = mean(Value, na.rm=T))$Value
  state_ts = ts(state_ts, start=c(2010,4), end=c(2014,11), frequency=12)

  # get time series of rent per sqft for each region in each city
  city_list = levels(df$City)
  for (c in city_list) {
    region_list = levels(factor(unlist(subset(df, City==c, "Region.Name"))))

    for (r in region_list) {
      # time window hard coded uniformaly for each region between 2012/02 to 2014/11
      r_df = subset(df, City==c & Region.Name==r)
      r_ts = ts(r_df$Value, start=c(2010,4), end=c(2014,11), frequency=12)
      # impute with global mean
      r_ts = imputeTS(r_ts, state_ts)
      r_future_ts = forecastTS(r_ts, nmonth_forecast)
      r_forecast_df = cbind(Region.Name=r,
                            City       =c,
                            State      =unique(r_df$State),
                            Metro      =unique(r_df$Metro),
                            County.Name=unique(r_df$County.Name),
                            r_future_ts)
      forecast_df = rbind(forecast_df, r_forecast_df)
    }
  }
  return(rbind(df_copy, forecast_df))
}

df = read.csv(ZRIfile)

# forecast rent per sqft for next decade
forecast120df = gen_forecastDF(df, 120)
# get point estimate at 0, 1, 5 and 10 year horizon
date_horizon = as.Date(c("2014-11-01", "2015-11-01", "2019-11-01", "2024-11-01"))
subdf = subset(forecast120df, City=="Seattle" & date %in% date_horizon)
write.table(subdf, 'Seattle_Neighborhood_Median_Rental_Price_Per_Sqft_All_Homes_forecast_0_1_5_10y.csv', row.names=F, col.names =T, quote=F, sep=",")
