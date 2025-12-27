from lpibydevcoder import run_code, Interpreter

interp = Interpreter()

run_code("x := 10", interp)
run_code("y := 20", interp)
run_code("pr(x + y)", interp)
run_code("pr(square(5))", interp)
