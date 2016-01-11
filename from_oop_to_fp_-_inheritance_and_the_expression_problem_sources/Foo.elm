module Foo where

import Base(Base(Base))

foo : Int -> Base
foo i = Base {step=(stepFoo i), display=(displayFoo i)}

-- Add delta to internal state.
stepFoo : Int -> Int -> Base
stepFoo i delta = foo <| i + delta

displayFoo : Int -> String
displayFoo i = show i