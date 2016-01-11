import Base(Base(Base))
import Foo(foo)
import Bar(bar)

stepOne : Base -> Base
stepOne (Base b) = b.step 1

-- Steps every object in l by 1.
stepAll : [Base] -> [Base]
stepAll l = map (\(Base b) -> b.step 1) l

-- Displays all objects in l beneath each other.
displayAll : [Base] -> String
displayAll l = concat (intersperse "\n" <| map (\(Base b) -> b.display) l)

main =
    let
        -- Fill a list with "derived instances".
        l : [Base]
        l = [foo 0, bar ""]

        -- Step every object two times.
        l' = (stepAll >> stepAll) l
    in
        -- Show result.
        plainText <| displayAll l'