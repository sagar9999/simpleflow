ESCAPE_SPECIAL = r"*+?\[](){}.^$|"
WDS_WD_SRNT = "wdsWDSAzrnt"
__author__ = 'zeb'

import unittest

# import re
from cdf.utils.regex_checking import *  # check, ParserState, Token


class BasicTests(unittest.TestCase):
    def test_empty(self):
        s = ""
        self.assertTrue(check(s))

    def test_simple(self):
        s = "toto"
        self.assertTrue(check(s))

    def test_parens(self):
        s = r"(abc)"
        self.assertTrue(check(s))

    def test_parens_open_1(self):
        s = r"abc("
        with self.assertRaises(RegexError):
            check(s)

    def test_parens_open_2(self):
        s = r"abc(def"
        with self.assertRaises(RegexError):
            check(s)

    def test_kleene_start(self):
        s = r"*"
        with self.assertRaises(RegexError):
            check(s)

    def test_kleene_double(self):
        s = r"*+"
        with self.assertRaises(RegexError):
            check(s)

    def test_kleene_double_2(self):
        s = r".**"
        with self.assertRaises(RegexError):
            check(s)

    def test_kleene_double_3_ok(self):
        s = r"(.*)*"
        self.assertTrue(check(s))

    def test_kleene_or(self):
        s = r"|+"
        with self.assertRaises(RegexError):
            check(s)

    def test_kleene_ok1(self):
        s = r"a+b*"
        self.assertTrue(check(s))

    def test_kleene_ok2(self):
        s = r"\d+\D*"
        self.assertTrue(check(s))

    def test_kleene_ok3(self):
        s = r"(xy)+(a|b)*"
        self.assertTrue(check(s))

    def test_kleene_ok4(self):
        s = r".+.*"
        self.assertTrue(check(s))

    def test_or_1(self):
        s = r"a|bc"
        self.assertTrue(check(s))

    def test_or_2(self):
        s = r"|"
        self.assertTrue(check(s))

    def test_qmark_alone(self):
        s = r"?"
        with self.assertRaises(RegexError):
            check(s)

    def test_qmark_two_for_nothing(self):
        s = r"??"
        with self.assertRaises(RegexError):
            check(s)

    def test_qmark_quantifier(self):
        s = r".?ab?"
        self.assertTrue(check(s))

    def test_qmark_modifier(self):
        s = r".*?ab+?"
        self.assertTrue(check(s))

    def test_qmark_quantifier_modifier(self):
        s = r".??"
        self.assertTrue(check(s))

    def test_qmark_tripled(self):
        s = r".???"
        with self.assertRaises(RegexError):
            check(s)

    def test_qmark_bad_modifier_again(self):
        s = r".+??"
        with self.assertRaises(RegexError):
            check(s)

    def test_qmark_tripled_parens(self):
        s = r"(.???)"
        with self.assertRaises(RegexError):
            check(s)

    def test_qmark_bad_modifier_again_parens(self):
        s = r"(.+??)"
        with self.assertRaises(RegexError):
            check(s)

    def test_brace_open(self):
        s = r"["
        with self.assertRaises(RegexError):
            check(s)

    def test_brace_open_parens(self):
        s = r"([)"
        with self.assertRaises(RegexError):
            check(s)

    def test_brace_open_neg(self):
        s = r"[^"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_empty(self):
        s = r"[]"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_empty_parens(self):
        s = r"([])"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_empty_neg(self):
        s = r"[^]"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_bracket_open(self):
        s = r"[[]"
        self.assertTrue(check(s))

    def test_class_bracket_closed(self):
        s = r"[]]"
        self.assertTrue(check(s))

    def test_class_bracket_closed_2(self):
        s = r"[\\]]"
        self.assertTrue(check(s))

    def test_class_bracket_open_ab(self):
        s = r"[[ab]"
        self.assertTrue(check(s))

    def test_class_bracket_closed_ab(self):
        s = r"[]ab]"
        self.assertTrue(check(s))

    def test_class_bracket_neg_open(self):
        s = r"[^[]"
        self.assertTrue(check(s))

    def test_class_bracket_neg_closed(self):
        s = r"[^]]"
        self.assertTrue(check(s))

    def test_class_bracket_neg_open_ab(self):
        s = r"[^[ab]"
        self.assertTrue(check(s))

    def test_class_bracket_neg_closed_ab(self):
        s = r"[^]ab]"
        self.assertTrue(check(s))

    def test_class_bracket_a(self):
        s = r"[a]"
        self.assertTrue(check(s))

    def test_class_bracket_abc(self):
        s = r"[abc]"
        self.assertTrue(check(s))

    def test_class_bracket_cba(self):
        s = r"[cba]"
        self.assertTrue(check(s))

    def test_class_bracket_atoc(self):
        s = r"[a-c]"
        self.assertTrue(check(s))

    def test_class_bracket_acto(self):
        s = r"[ac-]"
        self.assertTrue(check(s))

    def test_class_bracket_ctoa(self):
        s = r"[c-a]"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_bracket_cminusa(self):
        s = r"[c\-a]"
        self.assertTrue(check(s))

    def test_class_bracket_bs_1_ok(self):
        s = r"[abc\]]"
        self.assertTrue(check(s))

    def test_class_bracket_bs_2_unended(self):
        s = r"[abc\]"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_bracket_acAC(self):
        s = r"[a-cA-C]"
        self.assertTrue(check(s))

    def test_class_bracket_neg_abc(self):
        s = r"[^abc]"
        self.assertTrue(check(s))

    def test_class_alpha(self):
        s = r"[[:alpha:]]"
        with self.assertRaises(RegexError):
            check(s)

    def test_class_neg_upper(self):
        s = r"[[:^upper:]]"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_1(self):
        s = r"a{1}"
        self.assertTrue(check(s))

    def test_quantifier_1_more(self):
        s = r"a{1,}"
        self.assertTrue(check(s))

    def test_quantifier_1_2(self):
        s = r"a{1,2}"
        self.assertTrue(check(s))

    def test_quantifier_1_2_parens(self):
        s = r"(a){1,2}"
        self.assertTrue(check(s))

    def test_quantifier_1_2_qmark(self):
        s = r"a{1,2}?"
        self.assertTrue(check(s))

    def test_quantifier_on_nothing(self):
        s = r"{1,2}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_on_kleene(self):
        s = r"*{1,2}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_then_kleene(self):
        s = r"a{1,2}*"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_qmark_qmark(self):
        s = r"a{1,2}??"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_wrong_order(self):
        s = r"a{2,1}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_not_int(self):
        s = r"a{a,b}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_too_large(self):
        s = r"a{1001}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_m_too_large(self):
        s = r"a{1001,}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_n_too_large(self):
        s = r"a{0,1001}"
        with self.assertRaises(RegexError):
            check(s)

    def test_quantifier_on_anchor(self):
        s = r"${1}"
        self.assertTrue(check(s))

    def test_non_capturing(self):
        s = r"(?:...)"
        self.assertTrue(check(s))

    def test_non_capturing_2(self):
        s = r"(?:(\w+)(\d+?)[a-z]{1,3})"
        self.assertTrue(check(s))

    def test_named(self):
        s = r"(?P<name>...)"
        self.assertTrue(check(s))

    def test_named_star(self):
        s = r"(?P<name>...)*"
        self.assertTrue(check(s))

    def test_named_quant(self):
        s = r"(?P<name>...){2,}"
        self.assertTrue(check(s))

    def test_bad_ext_1(self):
        s = r"(?P<name...)"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_2(self):
        s = r"(?=...)"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_3(self):
        s = r"(?"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_4(self):
        s = r"(?)"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_5(self):
        s = r"(?P"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_6(self):
        s = r"(?P="
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_7(self):
        s = r"(?P<"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_8(self):
        s = r"(?P<a"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_9(self):
        s = r"(?P<a)"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_10(self):
        s = r"(?P<>"
        with self.assertRaises(RegexError):
            check(s)

    def test_bad_ext_11(self):
        s = r"(?P<>)"
        with self.assertRaises(RegexError):
            check(s)


class ParserStateTests(unittest.TestCase):
    def test_empty(self):
        ps = ParserState("")
        with self.assertRaises(StopIteration):
            ps.next()

    def test_simple(self):
        ps = ParserState("xy")
        x = ps.next()
        self.assertEqual((Token.Normal, 'x'), x)
        x = ps.next()
        self.assertEqual((Token.Normal, 'y'), x)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_escape_special(self):
        s = ESCAPE_SPECIAL
        s_escaped = '\\' + '\\'.join(s)
        ps = ParserState(s_escaped)
        # zz = list(zip(ps, s))
        for rx, x in zip(ps, s):
            self.assertEqual((Token.Normal, x), rx)

    def test_escape_eol(self):
        ps = ParserState("\\")
        x = ps.next()
        self.assertEqual((Token.BackslashAtEOLError, '\\'), x)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_known_escape(self):
        s = WDS_WD_SRNT
        s_escaped = '\\' + '\\'.join(s)
        ps = ParserState(s_escaped)
        # zz = list(zip(ps, s))
        for rx, x in zip(ps, s):
            self.assertEqual((Token.KnownEscape, x), rx)

    def test_unknown_escape(self):
        s = "xGpP%0123456789"
        s_escaped = '\\' + '\\'.join(s)
        ps = ParserState(s_escaped)
        # zz = list(zip(ps, s))
        for rx, x in zip(ps, s):
            self.assertEqual((Token.UnrecognizedEscapeError, x), rx)

    def test_unknown_escape_2(self):
        s = set((chr(i) for i in range(256)))
        s = s - set(WDS_WD_SRNT) - set(ESCAPE_SPECIAL)
        s_escaped = '\\' + '\\'.join(s)
        ps = ParserState(s_escaped)
        # zz = list(zip(ps, s))
        for rx, x in zip(ps, s):
            self.assertEqual((Token.UnrecognizedEscapeError, x), rx)

    def test_empty_parens(self):
        ps = ParserState("()")
        tok, c = ps.next()
        self.assertEqual(Token.GroupStart, tok)
        tok, c = ps.next()
        self.assertEqual(Token.GroupEnd, tok)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_left_parens(self):
        ps = ParserState("(")
        for rx in ps:
            self.assertEqual((Token.BadGroupError, None), rx)

    def test_right_parens(self):
        ps = ParserState(")")
        for rx in ps:
            self.assertEqual((Token.BadGroupError, None), rx)

    def test_right_parens_2(self):
        ps = ParserState("xxx)x")
        for tok, c in ps:
            if tok == Token.Normal:
                self.assertEqual('x', c)
            else:
                self.assertEqual(Token.BadGroupError, tok)

    def test_parens_nc(self):
        ps = ParserState(r" (?:a)")
        tok, e = ps.next()
        self.assertEqual(Token.Normal, tok)
        tok, e = ps.next()
        self.assertEqual(Token.GroupStart, tok)
        self.assertEqual(':', e)
        rx = ps.next()
        self.assertEqual((Token.Normal, 'a'), rx)
        tok, e = ps.next()
        self.assertEqual(Token.GroupEnd, tok)

    def test_parens_named(self):
        ps = ParserState(r" (?P<toto>a)")
        tok, e = ps.next()
        self.assertEqual(Token.Normal, tok)
        tok, e = ps.next()
        self.assertEqual(Token.GroupStart, tok)
        self.assertEqual('toto', e)
        rx = ps.next()
        self.assertEqual((Token.Normal, 'a'), rx)
        tok, e = ps.next()
        self.assertEqual(Token.GroupEnd, tok)

    def test_star(self):
        ps = ParserState("*")
        tok, c = ps.next()
        self.assertEqual(Token.Kleene, tok)
        self.assertEqual('*', c)

    def test_plus(self):
        ps = ParserState("+")
        tok, c = ps.next()
        self.assertEqual(Token.Kleene, tok)
        self.assertEqual('+', c)

    def test_bracket_open_1(self):
        s = r"["
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.BadClassError, tok)

    def test_bracket_open_2(self):
        s = r"[^"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.BadClassError, tok)

    def test_bracket_open_3(self):
        s = "[\\"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.BadClassError, tok)

    def test_bracket_open_4(self):
        s = "[a-"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.BadClassError, tok)

    def test_bracket_open_5(self):
        s = "[a-\\"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.BadClassError, tok)

    def test_bracket_closed(self):
        s = r"]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Normal, tok)
        self.assertEqual(']', c)

    def test_class_bracket_open(self):
        s = r"[[]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("[", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_closed(self):
        s = r"[]]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("]", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_bs_1(self):
        s = r"[abc\]]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("abc]", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_bs_2(self):
        s = r"[\]abc]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("]abc", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_range_1(self):
        s = r"[-abc]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("-abc", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_range_2(self):
        s = r"[abc-]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("abc-", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_range_3(self):
        s = r"[a-c]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("a-c", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_range_4(self):
        s = r"[a-c-a]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("a-c-a", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_range_5(self):
        s = r"[\[-\]]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("[-]", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_class_bracket_range_6(self):
        s = r"[\C-\A]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.BadClassError, tok)
        # Rest of line not checked
        # with self.assertRaises(StopIteration):
        # ps.next()

    def test_class_bracket_range_7(self):
        s = r"[---]"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Class, tok)
        self.assertIsInstance(c, CharClass)
        self.assertFalse(c.reverse)
        self.assertEqual("---", c.content)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_quantifier_1(self):
        s = r"{1}"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Quantifier, tok)
        self.assertIsInstance(c, int)
        self.assertEqual(1, c)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_quantifier_2(self):
        s = r"{1,}"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Quantifier, tok)
        self.assertIsInstance(c, tuple)
        self.assertEqual((1,), c)
        with self.assertRaises(StopIteration):
            ps.next()

    def test_quantifier_3(self):
        s = r"{1,2}"
        ps = ParserState(s)
        tok, c = ps.next()
        self.assertEqual(Token.Quantifier, tok)
        self.assertIsInstance(c, tuple)
        self.assertEqual((1, 2), c)
        with self.assertRaises(StopIteration):
            ps.next()


r"""
Run this in .../botify-cdf.
^d to quit.
PYTHONPATH=. python tests/utils/test_regex_checking.py

"""


def cli():
    import re
    # noinspection PyUnresolvedReferences
    import readline
    from cdf.utils.regex_checking import (check, RegexError)

    prompt = 'regex: '
    while 1:
        try:
            line = raw_input(prompt)
        except EOFError:
            print("EOF")
            break
        try:
            check(line)
            print("ok!")
            tmp = re.compile(line)
            del tmp
        except RegexError as x:
            print ('{}^ {}'.format('-' * (x.pos + len(prompt) - 1), x.token))


if __name__ == '__main__':
    cli()
