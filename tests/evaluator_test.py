# import unittest

# from prymate import evaluator, objects
# from prymate.scanner import Scanner
# from prymate.parser import Parser


# class TestEvaluator(unittest.TestCase):
#     def test_eval_numeric_exp(self):
#         tests = [
#             ["5", 5],
#             ["10", 10],
#             ["-5", -5],
#             ["-10", -10],
#             ["5 + 5 + 5 + 5 - 10", 10],
#             ["2 * 2 * 2 * 2 * 2", 32],
#             ["-50 + 100 + -50", 0],
#             ["5 * 2 + 10", 20],
#             ["5 + 2 * 10", 25],
#             ["20 + 2 * -10", 0],
#             ["50 / 2 * 2 + 10", 60],
#             ["2 * (5 + 10)", 30],
#             ["3 * 3 * 3 + 10", 37],
#             ["3 * (3 * 3) + 10", 37],
#             ["(5 + 10 * 2 + 15 / 3) * 2 + -10", 50],
#             ["2 * 3 % 4 * 2", 4],
#             ["2 * 3 % 4 * 2 - 10", -6],
#             ["2.2 * 2", 4.4],
#             ["12 / 6", 2.0],
#             ["12.2 / 2", 6.1],
#             ["1.5 * -1.5", -2.25],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             self._test_int_object(evaluated, tt[1])

#     def test_eval_bool_exp(self):
#         tests = [
#             ["true", True],
#             ["false", False],
#             ["1 < 2", True],
#             ["1 > 2", False],
#             ["1 < 1", False],
#             ["1 > 1", False],
#             ["1 == 1", True],
#             ["1 != 1", False],
#             ["1 == 2", False],
#             ["1 != 2", True],
#             ["true == true", True],
#             ["false == false", True],
#             ["true == false", False],
#             ["true != false", True],
#             ["false != true", True],
#             ["(1 < 2) == true", True],
#             ["(1 < 2) == false", False],
#             ["(1 > 2) == true", False],
#             ["(1 > 2) == false", True],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             self._test_boolean_object(evaluated, tt[1])

#     def test_bang_operator(self):
#         tests = [
#             ["!true", False],
#             ["!false", True],
#             ["!5", False],
#             ["!!true", True],
#             ["!!false", False],
#             ["!!5", True],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             self._test_boolean_object(evaluated, tt[1])

#     def test_if_exp(self):
#         tests = [
#             ["if (true) { 10 }", 10],
#             ["if (false) { 10 }", None],
#             ["if (1) { 10 }", 10],
#             ["if (1 < 2) { 10 }", 10],
#             ["if (1 > 2) { 10 }", None],
#             ["if (1 > 2) { 10 } else { 20 }", 20],
#             ["if (1 < 2) { 10 } else { 20 }", 10],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])

#             if isinstance(tt[1], int):
#                 self._test_int_object(evaluated, int(tt[1]))
#             else:
#                 self._test_null_object(evaluated)

#     def test_return_statements(self):
#         tests = [
#             ["return 10;", 10],
#             ["return 10; 9;", 10],
#             ["return 2 * 5; 9;", 10],
#             ["9; return 2 * 5; 9;", 10],
#             ["9; return 2 * 5.2; 9;", 10.4],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             self._test_int_object(evaluated, tt[1])

#     def test_error_handling(self):
#         tests = [
#             ["5 + true;", "type mismatch: INTEGER + BOOLEAN"],
#             ["5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"],
#             ["-true", "unknown operator: -BOOLEAN"],
#             ["true + false;", "unknown operator: BOOLEAN + BOOLEAN"],
#             ["true % false;", "unknown operator: BOOLEAN % BOOLEAN"],
#             ["5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN"],
#             ["if (10 > 1) { true + false; }", "unknown operator: BOOLEAN + BOOLEAN"],
#             [
#                 """
#             132
#             if (10 > 1) {
#             if (10 > 1) {
#             return true + false;
#             }
#             return 1;

#             """,
#                 "unknown operator: BOOLEAN + BOOLEAN",
#             ],
#             ["foobar", "identifier not found: foobar"],
#             ['"Hello" - "World"', "unknown operator: STRING - STRING"],
#             [
#                 '{"name": "Monkey"}[fn(x) { x }];',
#                 "unusable as dictionary key: FUNCTION",
#             ],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])

#             if not isinstance(evaluated, objects.Error):
#                 self.fail(f"No error object returned. Got {evaluated}.")

#             self.assertEqual(
#                 evaluated.message,
#                 tt[1],
#                 f"Wrong error message. Expected {tt[1]}, got {evaluated.message}.",
#             )

#     def test_let_statements(self):
#         tests = [
#             ["let a = 5; a;", 5],
#             ["let a = 5 * 5; a;", 25],
#             ["let a = 5; let b = a; b;", 5],
#             ["let a = 5; let b = a; let c = a + b + 5; c;", 15],
#         ]

#         for tt in tests:
#             self._test_int_object(self._test_eval(tt[0]), tt[1])

#     def test_function_object(self):
#         input_case = "fn(x) { x + 2; };"

#         evaluated = self._test_eval(input_case)
#         if not isinstance(evaluated, objects.Function):
#             self.fail(f"Object is not Function. Got, {evaluated}")

#         self.assertEqual(
#             len(evaluated.parameters),
#             1,
#             f"Function has wrong parameters, got {len(evaluated.parameters)}.",
#         )

#         self.assertEqual(
#             str(evaluated.parameters[0]),
#             "x",
#             f"Parameter is not 'x', got {str(evaluated.parameters[0])}.",
#         )

#         expected_body = "(x + 2)"
#         self.assertEqual(
#             str(evaluated.body),
#             expected_body,
#             f"body is not {expected_body}. got {str(evaluated.body)}.",
#         )

#     def test_function_application(self):
#         tests = [
#             ["let identity = fn(x) { x; }; identity(5);", 5],
#             ["let identity = fn(x) { return x; }; identity(5);", 5],
#             ["let double = fn(x) { x * 2; }; double(5);", 10],
#             ["let add = fn(x, y) { x + y; }; add(5, 5);", 10],
#             ["let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20],
#             ["fn(x) { x; }(5)", 5],
#         ]

#         for tt in tests:
#             self._test_int_object(self._test_eval(tt[0]), tt[1])

#     def test_string_literal(self):
#         input_case = '"Hello, World!"'

#         evaluated = self._test_eval(input_case)
#         if not isinstance(evaluated, objects.String):
#             self.fail(f"Object is not String, got {evaluated}.")

#         self.assertEqual(
#             evaluated.value,
#             "Hello, World!",
#             f"String has wrong value. Got {evaluated.value}.",
#         )

#     def test_string_concatenation(self):
#         input_case = '"Hello" + " " + "World!"'

#         evaluated = self._test_eval(input_case)
#         if not isinstance(evaluated, objects.String):
#             self.fail(f"Object is not String, got {evaluated}.")

#         self.assertEqual(
#             evaluated.value,
#             "Hello World!",
#             f"String has wrong value. Got {evaluated.value}.",
#         )

#     def test_builtin_functions(self):
#         tests = [
#             ['len("")', 0],
#             ['len("four")', 4],
#             ['len("hello world")', 11],
#             ["len(1)", "argument to `len` not supported, got INTEGER"],
#             ['len("one", "two")', "wrong number of arguments. got=2, want=1"],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             if isinstance(tt[1], int):
#                 self._test_int_object(evaluated, tt[1])
#             elif isinstance(tt[1], str):
#                 if not isinstance(evaluated, objects.Error):
#                     self.fail(f"Object not of type Error, got {evaluated.tp().value}.")

#                 self.assertEqual(
#                     evaluated.message,
#                     tt[1],
#                     f"Wrong error message. Expected={tt[1]}, Got={evaluated.message}.",
#                 )

#     def test_array_literals(self):
#         input_case = "[1, 2 * 2, 3 + 3];"
#         ev = self._test_eval(input_case)

#         if not isinstance(ev, objects.Array):
#             self.fail(f"Object not of type Array, got {ev.tp().value}.")

#         self.assertEqual(
#             len(ev.elements),
#             3,
#             f"Array has wrong number of elements. Got {len(ev.elements)}.",
#         )
#         self._test_int_object(ev.elements[0], 1)
#         self._test_int_object(ev.elements[1], 4)
#         self._test_int_object(ev.elements[2], 6)

#     def test_array_index_exp(self):
#         tests = [
#             ["[1, 2, 3][0]", 1],
#             ["[1, 2, 3][1]", 2],
#             ["[1, 2, 3][2]", 3],
#             ["let i = 0; [1][i];", 1],
#             ["[1, 2, 3][1 + 1];", 3],
#             ["let myArray = [1, 2, 3]; myArray[2];", 3],
#             ["let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6],
#             ["let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2],
#             ["[1, 2, 3][3]", None],
#             ["[1, 2, 3][-1]", None],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             if isinstance(tt[1], int):
#                 self._test_int_object(evaluated, tt[1])
#             else:
#                 self._test_null_object(evaluated)

#     def test_dictionary(self):
#         input_case = """
#         let two = "two";
#         {
#             "one": 10 - 9,
#             two: 1 + 1,
#             "thr" + "ee": 6 / 2,
#             4: 4,
#             true: 5,
#             false: 6
#         }
#         """

#         evaluated = self._test_eval(input_case)
#         if not isinstance(evaluated, objects.Dictionary):
#             self.fail(f"Eval didn't return Hash. Got {evaluated}.")

#         expected = {
#             objects.String("one").hashkey(): 1,
#             objects.String("two").hashkey(): 2,
#             objects.String("three").hashkey(): 3,
#             objects.Integer(4).hashkey(): 4,
#             objects.Boolean(True).hashkey(): 5,
#             objects.Boolean(False).hashkey(): 6,
#         }

#         self.assertEqual(
#             len(evaluated.pairs),
#             len(expected),
#             f"Hash has wrong num of pairs. Got {len(evaluated.pairs)}.",
#         )

#         for key, val in expected.items():
#             pair = evaluated.pairs.get(key, None)
#             self.assertNotEqual(pair, None, "No pair for given key in pairs")
#             self._test_int_object(pair.value, val)

#     def test_dict_index_exp(self):
#         tests = [
#             ['{"foo": 5}["foo"]', 5],
#             ['{"foo": 5}["bar"]', None],
#             ['let key = "foo"; {"foo": 5}[key]', 5],
#             ['{}["foo"]', None],
#             ["{5: 5}[5]", 5],
#             ["{true: 5}[true]", 5],
#             ["{false: 5}[false]", 5],
#         ]

#         for tt in tests:
#             evaluated = self._test_eval(tt[0])
#             integer = tt[1]
#             if integer is not None:
#                 self._test_int_object(evaluated, int(integer))
#             else:
#                 self._test_null_object(evaluated)

#     def _test_int_object(self, obj: objects.Object, expected: int):
#         if not isinstance(obj, objects.Integer) and not isinstance(obj, objects.Float):
#             self.fail(f"Expected object to be Integer/Float, got {type(obj)}.")

#         self.assertEqual(
#             obj.value,
#             expected,
#             f"Object has wrong value. Expected {expected}, got {obj.value}.",
#         )

#     def _test_boolean_object(self, obj: objects.Object, expected: bool):
#         if not isinstance(obj, objects.Boolean):
#             self.fail(f"Expected object to be Boolean, got {type(obj)}.")

#         self.assertEqual(
#             obj.value,
#             expected,
#             f"Object has wrong value. Expected {expected}, got {obj.value}.",
#         )

#     def _test_null_object(self, obj: objects.Object):
#         if obj is not objects.Null():
#             self.fail(f"Object is not NULL. Got {obj}.")

#     def _test_eval(self, input_case: str):
#         lexer = Scanner(input_case)
#         parser = Parser(lexer)
#         env = objects.Environment()

#         program = parser.parse_program()
#         return evaluator.evaluate(program, env)


# if __name__ == "__main__":
#     unittest.main()
