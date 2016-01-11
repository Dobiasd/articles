module Base where

data Base = Base {step : (Int -> Base), display : String}