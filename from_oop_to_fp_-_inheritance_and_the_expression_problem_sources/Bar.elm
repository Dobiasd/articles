module Bar where

import Base(Base(Base))

bar : String -> Base
bar s = Base {step=(stepBar s), display=(displayBar s)}

-- Concat delta as string to internal state.
stepBar : String -> Int -> Base
stepBar s delta = bar <| s ++ show delta

displayBar : String -> String
displayBar s = s