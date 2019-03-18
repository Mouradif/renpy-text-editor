# -*- coding: utf-8 -*-
"""
    RTE.syntaxhighlight.lexer
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexer for RenPy
    Based on the Python Lexer from the Pygments team.
"""

import re

from pygments.lexer import Lexer, RegexLexer, include, bygroups, using, \
    default, words, combined, do_insertions
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Generic, Other
from .tokens import Renpy, Block

__all__ = ['RenpyLexer', 'RenpyConsoleLexer', 'RenpyTracebackLexer']

line_re = re.compile('.*?\n')


class RenpyBlockLexer(RegexLexer):
    name = "RenpyBlock"
    aliases = ["renpyblock"]

    tokens = {
        'root': [
            (r'[a-zA-Z_]\w*', Name),
            (words((
                'elif', 'else', 'except', 'finally', 'for', 'if',
                'try', 'while', 'with', 'label', 'screen', 'transform',
                'init', 'layeredimage', 'menu', 'style'), suffix=r'\b'),
             Block.Start),
            (r'# *region\b', Block.Start),
            (r'# *endregion\b', Block.End),
            (words((
                '\n\n', 'break', 'continue', 'return', 'yield', 'yield from',
                'pass', '# *endregion'), suffix=r'\b'),
             Block.End),
        ],
    }


class RenpyLexer(RegexLexer):
    """
    For `Renpy <http://www.renpy.org>`_ source code.
    """

    name = 'Renpy'
    aliases = ['renpy', 'rpy']
    filenames = ['*.rpy']

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'\n', Text),
            include('screen_lang'),
            (r'^ *\$', Renpy.Python.Inline),
            (r'((renpy|im)\.[a-zA-Z_]+)\(([a-zA-Z_ ,=]+)\)',
             bygroups(Renpy.Function.Builtin, Renpy.Function.Arguments)),
            include("screen_actions"),
            (r'\$', String.Symbol),
            (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")',
             bygroups(Text, String.Affix, String.Doc)),
            (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
             bygroups(Text, String.Affix, String.Doc)),
            (r'[^\S\n]+', Text),
            (r'\A#!.+$', Comment.Hashbang),
            (r'#.*$', Comment.Single),
            (r'[]{}:(),;[]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            (r'(in|is|and|or|not)\b', Operator.Word),
            (r'!=|==|<<|>>|[-~+/*%=<>&^|.]', Operator),
            include('keywords'),
            include('special_labels'),
            (r'(def)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
            (r'(class)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'fromimport'),
            (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'import'),
            include('builtins'),
            include('magicfuncs'),
            include('magicvars'),
            include('backtick'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(""")',
             bygroups(String.Affix, String.Double), 'tdqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(''')",
             bygroups(String.Affix, String.Single), 'tsqs'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            ('([uUbB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            ("([uUbB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            include('name'),
            include('numbers'),
        ],
        'keywords': [
            (words((
                'assert', 'break', 'continue', 'del', 'elif', 'else', 'except',
                'exec', 'finally', 'for', 'global', 'if', 'lambda', 'pass',
                'print', 'raise', 'return', 'try', 'while', 'yield',
                'yield from', 'as', 'with'), suffix=r'\b'),
             Keyword),
            (words((
                'audio', 'scene', 'expression', 'play', 'queue', 'stop',
                'python', 'init', 'pause', 'jump', 'call', 'zorder',
                'show', 'hide', 'at', 'music', 'sound', 'voice',
            ), suffix=r'\b'), Renpy.Reserved),
            (words((
                'default', 'define', 'layeredimage', 'screen', 'transform',
                'label', 'menu', 'style', 'image'), suffix=r'\b'),
             Renpy.Declaration),
        ],
        'special_labels': [
            (words(('start', 'quit', 'after_load', 'splashscreen',
                    'before_main_menu', 'main_menu', 'after_warp',
                    ), prefix=r"label ", suffix=r'\b'), Renpy.Label.Reserved),
        ],
        'screen_lang': [
            (words(('add', 'bar', 'button', 'fixed', 'frame', 'grid',
                    'hbox', 'imagebutton', 'input', 'key',
                    'mousearea', 'null', 'side', 'text', 'textbutton',
                    'timer', 'vbar', 'vbox', 'viewport',
                    'vpgrid', 'window', 'imagemap', 'hotspot',
                    'hotbar', 'drag', 'draggroup', 'has', 'on', 'use',
                    'transclude', 'transform', 'label',
                    ), prefix=r'\s+', suffix=r'\b'), Renpy.Screen.Displayables),
        ],
        'properties': [  # renpy/tutorial/game/keywords.py
            (words(('action', 'activate_additive', 'activate_adjust_spacing', 'activate_align',
                    'activate_alignaround', 'activate_alpha', 'activate_alt', 'activate_anchor',
                    'activate_angle', 'activate_antialias', 'activate_area', 'activate_around',
                    'activate_background', 'activate_bar_invert', 'activate_bar_resizing',
                    'activate_bar_vertical', 'activate_base_bar', 'activate_black_color',
                    'activate_bold', 'activate_bottom_bar', 'activate_bottom_gutter',
                    'activate_bottom_margin', 'activate_bottom_padding', 'activate_box_layout',
                    'activate_box_reverse', 'activate_box_wrap', 'activate_box_wrap_spacing',
                    'activate_caret', 'activate_child', 'activate_clipping', 'activate_color',
                    'activate_corner1', 'activate_corner2', 'activate_crop', 'activate_crop_relative',
                    'activate_debug', 'activate_delay', 'activate_drop_shadow', 'activate_drop_shadow_color',
                    'activate_events', 'activate_first_indent', 'activate_first_spacing',
                    'activate_fit_first', 'activate_focus_mask', 'activate_font', 'activate_foreground',
                    'activate_hinting', 'activate_hyperlink_functions', 'activate_italic',
                    'activate_justify', 'activate_kerning', 'activate_key_events', 'activate_keyboard_focus',
                    'activate_language', 'activate_layout', 'activate_left_bar', 'activate_left_gutter',
                    'activate_left_margin', 'activate_left_padding', 'activate_line_leading',
                    'activate_line_spacing', 'activate_margin', 'activate_maximum', 'activate_maxsize',
                    'activate_min_width', 'activate_minimum', 'activate_minwidth', 'activate_mouse',
                    'activate_nearest', 'activate_newline_indent', 'activate_offset',
                    'activate_order_reverse', 'activate_outline_scaling', 'activate_outlines',
                    'activate_padding', 'activate_pos', 'activate_radius', 'activate_rest_indent',
                    'activate_right_bar', 'activate_right_gutter', 'activate_right_margin',
                    'activate_right_padding', 'activate_rotate', 'activate_rotate_pad',
                    'activate_ruby_style', 'activate_size', 'activate_size_group', 'activate_slow_abortable',
                    'activate_slow_cps', 'activate_slow_cps_multiplier', 'activate_sound', 'activate_spacing',
                    'activate_strikethrough', 'activate_subpixel', 'activate_text_align',
                    'activate_text_y_fudge', 'activate_thumb', 'activate_thumb_offset', 'activate_thumb_shadow',
                    'activate_tooltip', 'activate_top_bar', 'activate_top_gutter', 'activate_top_margin',
                    'activate_top_padding', 'activate_transform_anchor', 'activate_underline',
                    'activate_unscrollable', 'activate_vertical', 'activate_xalign', 'activate_xanchor',
                    'activate_xanchoraround', 'activate_xaround', 'activate_xcenter', 'activate_xfill',
                    'activate_xfit', 'activate_xmargin', 'activate_xmaximum', 'activate_xminimum',
                    'activate_xoffset', 'activate_xpadding', 'activate_xpan', 'activate_xpos',
                    'activate_xsize', 'activate_xspacing', 'activate_xtile', 'activate_xysize',
                    'activate_xzoom', 'activate_yalign', 'activate_yanchor', 'activate_yanchoraround',
                    'activate_yaround', 'activate_ycenter', 'activate_yfill', 'activate_yfit', 'activate_ymargin',
                    'activate_ymaximum', 'activate_yminimum', 'activate_yoffset', 'activate_ypadding',
                    'activate_ypan', 'activate_ypos', 'activate_ysize', 'activate_yspacing', 'activate_ytile',
                    'activate_yzoom', 'activate_zoom', 'activated', 'additive', 'adjust_spacing', 'adjustment',
                    'align', 'alignaround', 'allow', 'alpha', 'alt', 'alternate', 'alternate_keysym', 'anchor',
                    'angle', 'antialias', 'area', 'arguments', 'around', 'arrowkeys', 'background',
                    'bar_invert', 'bar_resizing', 'bar_vertical', 'base_bar', 'black_color', 'bold',
                    'bottom_bar', 'bottom_gutter', 'bottom_margin', 'bottom_padding', 'box_layout',
                    'box_reverse', 'box_wrap', 'box_wrap_spacing', 'cache', u'caption', 'caret', 'changed',
                    'child', 'child_size', 'clicked', 'clipping', 'color', 'cols', 'copypaste', 'corner1',
                    'corner2', 'crop', 'crop_relative', 'debug', 'delay', 'drag_handle', 'drag_joined',
                    'drag_name', 'drag_offscreen', 'drag_raise', 'draggable', 'dragged', 'drop_allowable',
                    'drop_shadow', 'drop_shadow_color', 'droppable', 'dropped', 'edgescroll', 'events',
                    'exclude', 'first_indent', 'first_spacing', 'fit_first', 'focus', 'focus_mask', 'font',
                    'foreground', 'ground', 'height', 'hinting', 'hover', 'hover_additive',
                    'hover_adjust_spacing', 'hover_align', 'hover_alignaround', 'hover_alpha', 'hover_alt',
                    'hover_anchor', 'hover_angle', 'hover_antialias', 'hover_area', 'hover_around',
                    'hover_background', 'hover_bar_invert', 'hover_bar_resizing', 'hover_bar_vertical',
                    'hover_base_bar', 'hover_black_color', 'hover_bold', 'hover_bottom_bar', 'hover_bottom_gutter',
                    'hover_bottom_margin', 'hover_bottom_padding', 'hover_box_layout', 'hover_box_reverse',
                    'hover_box_wrap', 'hover_box_wrap_spacing', 'hover_caret', 'hover_child', 'hover_clipping',
                    'hover_color', 'hover_corner1', 'hover_corner2', 'hover_crop', 'hover_crop_relative',
                    'hover_debug', 'hover_delay', 'hover_drop_shadow', 'hover_drop_shadow_color', 'hover_events',
                    'hover_first_indent', 'hover_first_spacing', 'hover_fit_first', 'hover_focus_mask',
                    'hover_font', 'hover_foreground', 'hover_hinting', 'hover_hyperlink_functions', 'hover_italic',
                    'hover_justify', 'hover_kerning', 'hover_key_events', 'hover_keyboard_focus', 'hover_language',
                    'hover_layout', 'hover_left_bar', 'hover_left_gutter', 'hover_left_margin',
                    'hover_left_padding', 'hover_line_leading', 'hover_line_spacing', 'hover_margin',
                    'hover_maximum', 'hover_maxsize', 'hover_min_width', 'hover_minimum', 'hover_minwidth',
                    'hover_mouse', 'hover_nearest', 'hover_newline_indent', 'hover_offset', 'hover_order_reverse',
                    'hover_outline_scaling', 'hover_outlines', 'hover_padding', 'hover_pos', 'hover_radius',
                    'hover_rest_indent', 'hover_right_bar', 'hover_right_gutter', 'hover_right_margin',
                    'hover_right_padding', 'hover_rotate', 'hover_rotate_pad', 'hover_ruby_style', 'hover_size',
                    'hover_size_group', 'hover_slow_abortable', 'hover_slow_cps', 'hover_slow_cps_multiplier',
                    'hover_sound', 'hover_spacing', 'hover_strikethrough', 'hover_subpixel',
                    'hover_text_align', 'hover_text_y_fudge', 'hover_thumb', 'hover_thumb_offset',
                    'hover_thumb_shadow', 'hover_tooltip', 'hover_top_bar', 'hover_top_gutter',
                    'hover_top_margin', 'hover_top_padding', 'hover_transform_anchor', 'hover_underline',
                    'hover_unscrollable', 'hover_vertical', 'hover_xalign', 'hover_xanchor',
                    'hover_xanchoraround', 'hover_xaround', 'hover_xcenter', 'hover_xfill', 'hover_xfit',
                    'hover_xmargin', 'hover_xmaximum', 'hover_xminimum', 'hover_xoffset', 'hover_xpadding',
                    'hover_xpan', 'hover_xpos', 'hover_xsize', 'hover_xspacing', 'hover_xtile', 'hover_xysize',
                    'hover_xzoom', 'hover_yalign', 'hover_yanchor', 'hover_yanchoraround', 'hover_yaround',
                    'hover_ycenter', 'hover_yfill', 'hover_yfit', 'hover_ymargin', 'hover_ymaximum',
                    'hover_yminimum', 'hover_yoffset', 'hover_ypadding', 'hover_ypan', 'hover_ypos', 'hover_ysize',
                    'hover_yspacing', 'hover_ytile', 'hover_yzoom', 'hover_zoom', 'hovered', 'hyperlink_functions',
                    'id', 'idle', 'idle_additive', 'idle_adjust_spacing', 'idle_align', 'idle_alignaround',
                    'idle_alpha', 'idle_alt', 'idle_anchor', 'idle_angle', 'idle_antialias', 'idle_area',
                    'idle_around', 'idle_background', 'idle_bar_invert', 'idle_bar_resizing', 'idle_bar_vertical',
                    'idle_base_bar', 'idle_black_color', 'idle_bold', 'idle_bottom_bar', 'idle_bottom_gutter',
                    'idle_bottom_margin', 'idle_bottom_padding', 'idle_box_layout', 'idle_box_reverse',
                    'idle_box_wrap', 'idle_box_wrap_spacing', 'idle_caret', 'idle_child', 'idle_clipping',
                    'idle_color', 'idle_corner1', 'idle_corner2', 'idle_crop', 'idle_crop_relative', 'idle_debug',
                    'idle_delay', 'idle_drop_shadow', 'idle_drop_shadow_color', 'idle_events',
                    'idle_first_indent', 'idle_first_spacing', 'idle_fit_first', 'idle_focus_mask', 'idle_font',
                    'idle_foreground', 'idle_hinting', 'idle_hyperlink_functions', 'idle_italic', 'idle_justify',
                    'idle_kerning', 'idle_key_events', 'idle_keyboard_focus', 'idle_language', 'idle_layout',
                    'idle_left_bar', 'idle_left_gutter', 'idle_left_margin', 'idle_left_padding',
                    'idle_line_leading', 'idle_line_spacing', 'idle_margin', 'idle_maximum', 'idle_maxsize',
                    'idle_min_width', 'idle_minimum', 'idle_minwidth', 'idle_mouse', 'idle_nearest',
                    'idle_newline_indent', 'idle_offset', 'idle_order_reverse', 'idle_outline_scaling',
                    'idle_outlines', 'idle_padding', 'idle_pos', 'idle_radius', 'idle_rest_indent',
                    'idle_right_bar', 'idle_right_gutter', 'idle_right_margin', 'idle_right_padding',
                    'idle_rotate', 'idle_rotate_pad', 'idle_ruby_style', 'idle_size', 'idle_size_group',
                    'idle_slow_abortable', 'idle_slow_cps', 'idle_slow_cps_multiplier', 'idle_sound',
                    'idle_spacing', 'idle_strikethrough', 'idle_subpixel', 'idle_text_align', 'idle_text_y_fudge',
                    'idle_thumb', 'idle_thumb_offset', 'idle_thumb_shadow', 'idle_tooltip', 'idle_top_bar',
                    'idle_top_gutter', 'idle_top_margin', 'idle_top_padding', 'idle_transform_anchor',
                    'idle_underline', 'idle_unscrollable', 'idle_vertical', 'idle_xalign', 'idle_xanchor',
                    'idle_xanchoraround', 'idle_xaround', 'idle_xcenter', 'idle_xfill', 'idle_xfit',
                    'idle_xmargin', 'idle_xmaximum', 'idle_xminimum', 'idle_xoffset', 'idle_xpadding',
                    'idle_xpan', 'idle_xpos', 'idle_xsize', 'idle_xspacing', 'idle_xtile', 'idle_xysize',
                    'idle_xzoom', 'idle_yalign', 'idle_yanchor', 'idle_yanchoraround', 'idle_yaround',
                    'idle_ycenter', 'idle_yfill', 'idle_yfit', 'idle_ymargin', 'idle_ymaximum', 'idle_yminimum',
                    'idle_yoffset', 'idle_ypadding', 'idle_ypan', 'idle_ypos', 'idle_ysize', 'idle_yspacing',
                    'idle_ytile', 'idle_yzoom', 'idle_zoom', 'image_style', 'insensitive', 'insensitive_additive',
                    'insensitive_adjust_spacing', 'insensitive_align', 'insensitive_alignaround',
                    'insensitive_alpha', 'insensitive_alt', 'insensitive_anchor', 'insensitive_angle',
                    'insensitive_antialias', 'insensitive_area', 'insensitive_around', 'insensitive_background',
                    'insensitive_bar_invert', 'insensitive_bar_resizing', 'insensitive_bar_vertical', 'insensitive_base_bar',
                    'insensitive_black_color', 'insensitive_bold', 'insensitive_bottom_bar', 'insensitive_bottom_gutter',
                    'insensitive_bottom_margin', 'insensitive_bottom_padding', 'insensitive_box_layout', 'insensitive_box_reverse',
                    'insensitive_box_wrap', 'insensitive_box_wrap_spacing', 'insensitive_caret', 'insensitive_child',
                    'insensitive_clipping', 'insensitive_color', 'insensitive_corner1', 'insensitive_corner2', 'insensitive_crop',
                    'insensitive_crop_relative', 'insensitive_debug', 'insensitive_delay', 'insensitive_drop_shadow',
                    'insensitive_drop_shadow_color', 'insensitive_events', 'insensitive_first_indent', 'insensitive_first_spacing',
                    'insensitive_fit_first', 'insensitive_focus_mask', 'insensitive_font', 'insensitive_foreground',
                    'insensitive_hinting', 'insensitive_hyperlink_functions', 'insensitive_italic', 'insensitive_justify',
                    'insensitive_kerning', 'insensitive_key_events', 'insensitive_keyboard_focus', 'insensitive_language',
                    'insensitive_layout', 'insensitive_left_bar', 'insensitive_left_gutter', 'insensitive_left_margin',
                    'insensitive_left_padding', 'insensitive_line_leading', 'insensitive_line_spacing', 'insensitive_margin',
                    'insensitive_maximum', 'insensitive_maxsize', 'insensitive_min_width', 'insensitive_minimum',
                    'insensitive_minwidth', 'insensitive_mouse', 'insensitive_nearest', 'insensitive_newline_indent',
                    'insensitive_offset', 'insensitive_order_reverse', 'insensitive_outline_scaling', 'insensitive_outlines',
                    'insensitive_padding', 'insensitive_pos', 'insensitive_radius', 'insensitive_rest_indent',
                    'insensitive_right_bar', 'insensitive_right_gutter', 'insensitive_right_margin', 'insensitive_right_padding',
                    'insensitive_rotate', 'insensitive_rotate_pad', 'insensitive_ruby_style', 'insensitive_size',
                    'insensitive_size_group', 'insensitive_slow_abortable', 'insensitive_slow_cps', 'insensitive_slow_cps_multiplier',
                    'insensitive_sound', 'insensitive_spacing', 'insensitive_strikethrough', 'insensitive_subpixel',
                    'insensitive_text_align', 'insensitive_text_y_fudge', 'insensitive_thumb', 'insensitive_thumb_offset',
                    'insensitive_thumb_shadow', 'insensitive_tooltip', 'insensitive_top_bar', 'insensitive_top_gutter',
                    'insensitive_top_margin', 'insensitive_top_padding', 'insensitive_transform_anchor', 'insensitive_underline',
                    'insensitive_unscrollable', 'insensitive_vertical', 'insensitive_xalign', 'insensitive_xanchor',
                    'insensitive_xanchoraround', 'insensitive_xaround', 'insensitive_xcenter', 'insensitive_xfill',
                    'insensitive_xfit', 'insensitive_xmargin', 'insensitive_xmaximum', 'insensitive_xminimum', 'insensitive_xoffset',
                    'insensitive_xpadding', 'insensitive_xpan', 'insensitive_xpos', 'insensitive_xsize', 'insensitive_xspacing',
                    'insensitive_xtile', 'insensitive_xysize', 'insensitive_xzoom', 'insensitive_yalign', 'insensitive_yanchor',
                    'insensitive_yanchoraround', 'insensitive_yaround', 'insensitive_ycenter', 'insensitive_yfill', 'insensitive_yfit',
                    'insensitive_ymargin', 'insensitive_ymaximum', 'insensitive_yminimum', 'insensitive_yoffset',
                    'insensitive_ypadding', 'insensitive_ypan', 'insensitive_ypos', 'insensitive_ysize', 'insensitive_yspacing',
                    'insensitive_ytile', 'insensitive_yzoom', 'insensitive_zoom', 'italic', 'justify', 'kerning', 'key_events',
                    'keyboard_focus', 'keysym', 'language', 'layer', 'layout', 'left_bar', 'left_gutter', 'left_margin',
                    'left_padding', 'length', 'line_leading', 'line_spacing', 'margin', 'maximum', 'maxsize', 'min_overlap',
                    'min_width', 'minimum', 'minwidth', 'modal', 'mouse', 'mouse_drop', 'mousewheel', 'nearest', 'newline_indent',
                    'order_reverse', 'outline_scaling', 'outlines', 'padding', 'pagekeys', 'pixel_width', 'pos', 'predict', 'prefix',
                    'properties', 'radius', 'range', 'rest_indent', 'right_bar', 'right_gutter', 'right_margin', 'right_padding',
                    'rotate', 'rotate_pad', 'rows', 'ruby_style', 'scope', 'scrollbar_activate_align', 'scrollbar_activate_alt',
                    'scrollbar_activate_anchor', 'scrollbar_activate_area', 'scrollbar_activate_bar_invert',
                    'scrollbar_activate_bar_resizing', 'scrollbar_activate_bar_vertical', 'scrollbar_activate_base_bar',
                    'scrollbar_activate_bottom_bar', 'scrollbar_activate_bottom_gutter', 'scrollbar_activate_clipping',
                    'scrollbar_activate_debug', 'scrollbar_activate_keyboard_focus', 'scrollbar_activate_left_bar',
                    'scrollbar_activate_left_gutter', 'scrollbar_activate_maximum', 'scrollbar_activate_mouse',
                    'scrollbar_activate_offset', 'scrollbar_activate_pos', 'scrollbar_activate_right_bar',
                    'scrollbar_activate_right_gutter', 'scrollbar_activate_thumb', 'scrollbar_activate_thumb_offset',
                    'scrollbar_activate_thumb_shadow', 'scrollbar_activate_tooltip', 'scrollbar_activate_top_bar',
                    'scrollbar_activate_top_gutter', 'scrollbar_activate_unscrollable', 'scrollbar_activate_xalign',
                    'scrollbar_activate_xanchor', 'scrollbar_activate_xcenter', 'scrollbar_activate_xfill',
                    'scrollbar_activate_xmaximum', 'scrollbar_activate_xoffset', 'scrollbar_activate_xpos',
                    'scrollbar_activate_xsize', 'scrollbar_activate_xysize', 'scrollbar_activate_yalign',
                    'scrollbar_activate_yanchor', 'scrollbar_activate_ycenter', 'scrollbar_activate_yfill',
                    'scrollbar_activate_ymaximum', 'scrollbar_activate_yoffset', 'scrollbar_activate_ypos',
                    'scrollbar_activate_ysize', 'scrollbar_align', 'scrollbar_alt', 'scrollbar_anchor',
                    'scrollbar_area', 'scrollbar_bar_invert', 'scrollbar_bar_resizing', 'scrollbar_bar_vertical',
                    'scrollbar_base_bar', 'scrollbar_bottom_bar', 'scrollbar_bottom_gutter', 'scrollbar_clipping',
                    'scrollbar_debug', 'scrollbar_hover_align', 'scrollbar_hover_alt', 'scrollbar_hover_anchor',
                    'scrollbar_hover_area', 'scrollbar_hover_bar_invert', 'scrollbar_hover_bar_resizing',
                    'scrollbar_hover_bar_vertical', 'scrollbar_hover_base_bar', 'scrollbar_hover_bottom_bar',
                    'scrollbar_hover_bottom_gutter', 'scrollbar_hover_clipping', 'scrollbar_hover_debug',
                    'scrollbar_hover_keyboard_focus', 'scrollbar_hover_left_bar', 'scrollbar_hover_left_gutter',
                    'scrollbar_hover_maximum', 'scrollbar_hover_mouse', 'scrollbar_hover_offset', 'scrollbar_hover_pos',
                    'scrollbar_hover_right_bar', 'scrollbar_hover_right_gutter', 'scrollbar_hover_thumb',
                    'scrollbar_hover_thumb_offset', 'scrollbar_hover_thumb_shadow', 'scrollbar_hover_tooltip',
                    'scrollbar_hover_top_bar', 'scrollbar_hover_top_gutter', 'scrollbar_hover_unscrollable',
                    'scrollbar_hover_xalign', 'scrollbar_hover_xanchor', 'scrollbar_hover_xcenter',
                    'scrollbar_hover_xfill', 'scrollbar_hover_xmaximum', 'scrollbar_hover_xoffset', 'scrollbar_hover_xpos',
                    'scrollbar_hover_xsize', 'scrollbar_hover_xysize', 'scrollbar_hover_yalign', 'scrollbar_hover_yanchor',
                    'scrollbar_hover_ycenter', 'scrollbar_hover_yfill', 'scrollbar_hover_ymaximum',
                    'scrollbar_hover_yoffset', 'scrollbar_hover_ypos', 'scrollbar_hover_ysize', 'scrollbar_idle_align',
                    'scrollbar_idle_alt', 'scrollbar_idle_anchor', 'scrollbar_idle_area', 'scrollbar_idle_bar_invert',
                    'scrollbar_idle_bar_resizing', 'scrollbar_idle_bar_vertical', 'scrollbar_idle_base_bar',
                    'scrollbar_idle_bottom_bar', 'scrollbar_idle_bottom_gutter', 'scrollbar_idle_clipping',
                    'scrollbar_idle_debug', 'scrollbar_idle_keyboard_focus', 'scrollbar_idle_left_bar',
                    'scrollbar_idle_left_gutter', 'scrollbar_idle_maximum', 'scrollbar_idle_mouse',
                    'scrollbar_idle_offset', 'scrollbar_idle_pos', 'scrollbar_idle_right_bar', 'scrollbar_idle_right_gutter',
                    'scrollbar_idle_thumb', 'scrollbar_idle_thumb_offset', 'scrollbar_idle_thumb_shadow', 'scrollbar_idle_tooltip',
                    'scrollbar_idle_top_bar', 'scrollbar_idle_top_gutter', 'scrollbar_idle_unscrollable', 'scrollbar_idle_xalign',
                    'scrollbar_idle_xanchor', 'scrollbar_idle_xcenter', 'scrollbar_idle_xfill', 'scrollbar_idle_xmaximum',
                    'scrollbar_idle_xoffset', 'scrollbar_idle_xpos', 'scrollbar_idle_xsize', 'scrollbar_idle_xysize',
                    'scrollbar_idle_yalign', 'scrollbar_idle_yanchor', 'scrollbar_idle_ycenter', 'scrollbar_idle_yfill',
                    'scrollbar_idle_ymaximum', 'scrollbar_idle_yoffset', 'scrollbar_idle_ypos', 'scrollbar_idle_ysize',
                    'scrollbar_insensitive_align', 'scrollbar_insensitive_alt', 'scrollbar_insensitive_anchor',
                    'scrollbar_insensitive_area', 'scrollbar_insensitive_bar_invert', 'scrollbar_insensitive_bar_resizing',
                    'scrollbar_insensitive_bar_vertical', 'scrollbar_insensitive_base_bar', 'scrollbar_insensitive_bottom_bar',
                    'scrollbar_insensitive_bottom_gutter', 'scrollbar_insensitive_clipping', 'scrollbar_insensitive_debug',
                    'scrollbar_insensitive_keyboard_focus', 'scrollbar_insensitive_left_bar', 'scrollbar_insensitive_left_gutter',
                    'scrollbar_insensitive_maximum', 'scrollbar_insensitive_mouse', 'scrollbar_insensitive_offset',
                    'scrollbar_insensitive_pos', 'scrollbar_insensitive_right_bar', 'scrollbar_insensitive_right_gutter',
                    'scrollbar_insensitive_thumb', 'scrollbar_insensitive_thumb_offset', 'scrollbar_insensitive_thumb_shadow',
                    'scrollbar_insensitive_tooltip', 'scrollbar_insensitive_top_bar', 'scrollbar_insensitive_top_gutter',
                    'scrollbar_insensitive_unscrollable', 'scrollbar_insensitive_xalign', 'scrollbar_insensitive_xanchor',
                    'scrollbar_insensitive_xcenter', 'scrollbar_insensitive_xfill', 'scrollbar_insensitive_xmaximum',
                    'scrollbar_insensitive_xoffset', 'scrollbar_insensitive_xpos', 'scrollbar_insensitive_xsize',
                    'scrollbar_insensitive_xysize', 'scrollbar_insensitive_yalign', 'scrollbar_insensitive_yanchor',
                    'scrollbar_insensitive_ycenter', 'scrollbar_insensitive_yfill', 'scrollbar_insensitive_ymaximum',
                    'scrollbar_insensitive_yoffset', 'scrollbar_insensitive_ypos', 'scrollbar_insensitive_ysize',
                    'scrollbar_keyboard_focus', 'scrollbar_left_bar', 'scrollbar_left_gutter', 'scrollbar_maximum',
                    'scrollbar_mouse', 'scrollbar_offset', 'scrollbar_pos', 'scrollbar_right_bar', 'scrollbar_right_gutter',
                    'scrollbar_selected_activate_align', 'scrollbar_selected_activate_alt', 'scrollbar_selected_activate_anchor',
                    'scrollbar_selected_activate_area', 'scrollbar_selected_activate_bar_invert',
                    'scrollbar_selected_activate_bar_resizing', 'scrollbar_selected_activate_bar_vertical',
                    'scrollbar_selected_activate_base_bar', 'scrollbar_selected_activate_bottom_bar',
                    'scrollbar_selected_activate_bottom_gutter', 'scrollbar_selected_activate_clipping',
                    'scrollbar_selected_activate_debug', 'scrollbar_selected_activate_keyboard_focus',
                    'scrollbar_selected_activate_left_bar', 'scrollbar_selected_activate_left_gutter',
                    'scrollbar_selected_activate_maximum', 'scrollbar_selected_activate_mouse', 'scrollbar_selected_activate_offset',
                    'scrollbar_selected_activate_pos', 'scrollbar_selected_activate_right_bar',
                    'scrollbar_selected_activate_right_gutter', 'scrollbar_selected_activate_thumb',
                    'scrollbar_selected_activate_thumb_offset', 'scrollbar_selected_activate_thumb_shadow',
                    'scrollbar_selected_activate_tooltip', 'scrollbar_selected_activate_top_bar',
                    'scrollbar_selected_activate_top_gutter', 'scrollbar_selected_activate_unscrollable',
                    'scrollbar_selected_activate_xalign', 'scrollbar_selected_activate_xanchor',
                    'scrollbar_selected_activate_xcenter', 'scrollbar_selected_activate_xfill',
                    'scrollbar_selected_activate_xmaximum', 'scrollbar_selected_activate_xoffset',
                    'scrollbar_selected_activate_xpos', 'scrollbar_selected_activate_xsize', 'scrollbar_selected_activate_xysize',
                    'scrollbar_selected_activate_yalign', 'scrollbar_selected_activate_yanchor', 'scrollbar_selected_activate_ycenter',
                    'scrollbar_selected_activate_yfill', 'scrollbar_selected_activate_ymaximum', 'scrollbar_selected_activate_yoffset', 'scrollbar_selected_activate_ypos', 'scrollbar_selected_activate_ysize', 'scrollbar_selected_align', 'scrollbar_selected_alt', 'scrollbar_selected_anchor', 'scrollbar_selected_area', 'scrollbar_selected_bar_invert', 'scrollbar_selected_bar_resizing', 'scrollbar_selected_bar_vertical', 'scrollbar_selected_base_bar', 'scrollbar_selected_bottom_bar', 'scrollbar_selected_bottom_gutter', 'scrollbar_selected_clipping', 'scrollbar_selected_debug', 'scrollbar_selected_hover_align', 'scrollbar_selected_hover_alt', 'scrollbar_selected_hover_anchor', 'scrollbar_selected_hover_area', 'scrollbar_selected_hover_bar_invert', 'scrollbar_selected_hover_bar_resizing', 'scrollbar_selected_hover_bar_vertical', 'scrollbar_selected_hover_base_bar', 'scrollbar_selected_hover_bottom_bar', 'scrollbar_selected_hover_bottom_gutter', 'scrollbar_selected_hover_clipping', 'scrollbar_selected_hover_debug', 'scrollbar_selected_hover_keyboard_focus', 'scrollbar_selected_hover_left_bar', 'scrollbar_selected_hover_left_gutter', 'scrollbar_selected_hover_maximum', 'scrollbar_selected_hover_mouse', 'scrollbar_selected_hover_offset', 'scrollbar_selected_hover_pos', 'scrollbar_selected_hover_right_bar', 'scrollbar_selected_hover_right_gutter', 'scrollbar_selected_hover_thumb', 'scrollbar_selected_hover_thumb_offset', 'scrollbar_selected_hover_thumb_shadow', 'scrollbar_selected_hover_tooltip', 'scrollbar_selected_hover_top_bar', 'scrollbar_selected_hover_top_gutter', 'scrollbar_selected_hover_unscrollable', 'scrollbar_selected_hover_xalign', 'scrollbar_selected_hover_xanchor', 'scrollbar_selected_hover_xcenter', 'scrollbar_selected_hover_xfill', 'scrollbar_selected_hover_xmaximum', 'scrollbar_selected_hover_xoffset', 'scrollbar_selected_hover_xpos', 'scrollbar_selected_hover_xsize', 'scrollbar_selected_hover_xysize', 'scrollbar_selected_hover_yalign', 'scrollbar_selected_hover_yanchor', 'scrollbar_selected_hover_ycenter', 'scrollbar_selected_hover_yfill', 'scrollbar_selected_hover_ymaximum', 'scrollbar_selected_hover_yoffset', 'scrollbar_selected_hover_ypos', 'scrollbar_selected_hover_ysize', 'scrollbar_selected_idle_align', 'scrollbar_selected_idle_alt', 'scrollbar_selected_idle_anchor', 'scrollbar_selected_idle_area', 'scrollbar_selected_idle_bar_invert', 'scrollbar_selected_idle_bar_resizing', 'scrollbar_selected_idle_bar_vertical', 'scrollbar_selected_idle_base_bar', 'scrollbar_selected_idle_bottom_bar', 'scrollbar_selected_idle_bottom_gutter', 'scrollbar_selected_idle_clipping', 'scrollbar_selected_idle_debug', 'scrollbar_selected_idle_keyboard_focus', 'scrollbar_selected_idle_left_bar', 'scrollbar_selected_idle_left_gutter', 'scrollbar_selected_idle_maximum', 'scrollbar_selected_idle_mouse', 'scrollbar_selected_idle_offset', 'scrollbar_selected_idle_pos', 'scrollbar_selected_idle_right_bar', 'scrollbar_selected_idle_right_gutter', 'scrollbar_selected_idle_thumb', 'scrollbar_selected_idle_thumb_offset', 'scrollbar_selected_idle_thumb_shadow', 'scrollbar_selected_idle_tooltip', 'scrollbar_selected_idle_top_bar', 'scrollbar_selected_idle_top_gutter', 'scrollbar_selected_idle_unscrollable', 'scrollbar_selected_idle_xalign', 'scrollbar_selected_idle_xanchor', 'scrollbar_selected_idle_xcenter', 'scrollbar_selected_idle_xfill', 'scrollbar_selected_idle_xmaximum', 'scrollbar_selected_idle_xoffset', 'scrollbar_selected_idle_xpos', 'scrollbar_selected_idle_xsize', 'scrollbar_selected_idle_xysize', 'scrollbar_selected_idle_yalign', 'scrollbar_selected_idle_yanchor', 'scrollbar_selected_idle_ycenter', 'scrollbar_selected_idle_yfill', 'scrollbar_selected_idle_ymaximum', 'scrollbar_selected_idle_yoffset', 'scrollbar_selected_idle_ypos', 'scrollbar_selected_idle_ysize', 'scrollbar_selected_insensitive_align', 'scrollbar_selected_insensitive_alt', 'scrollbar_selected_insensitive_anchor', 'scrollbar_selected_insensitive_area', 'scrollbar_selected_insensitive_bar_invert', 'scrollbar_selected_insensitive_bar_resizing', 'scrollbar_selected_insensitive_bar_vertical', 'scrollbar_selected_insensitive_base_bar', 'scrollbar_selected_insensitive_bottom_bar', 'scrollbar_selected_insensitive_bottom_gutter', 'scrollbar_selected_insensitive_clipping', 'scrollbar_selected_insensitive_debug', 'scrollbar_selected_insensitive_keyboard_focus', 'scrollbar_selected_insensitive_left_bar', 'scrollbar_selected_insensitive_left_gutter', 'scrollbar_selected_insensitive_maximum', 'scrollbar_selected_insensitive_mouse', 'scrollbar_selected_insensitive_offset', 'scrollbar_selected_insensitive_pos', 'scrollbar_selected_insensitive_right_bar', 'scrollbar_selected_insensitive_right_gutter', 'scrollbar_selected_insensitive_thumb', 'scrollbar_selected_insensitive_thumb_offset', 'scrollbar_selected_insensitive_thumb_shadow', 'scrollbar_selected_insensitive_tooltip', 'scrollbar_selected_insensitive_top_bar', 'scrollbar_selected_insensitive_top_gutter', 'scrollbar_selected_insensitive_unscrollable', 'scrollbar_selected_insensitive_xalign', 'scrollbar_selected_insensitive_xanchor', 'scrollbar_selected_insensitive_xcenter', 'scrollbar_selected_insensitive_xfill', 'scrollbar_selected_insensitive_xmaximum', 'scrollbar_selected_insensitive_xoffset', 'scrollbar_selected_insensitive_xpos', 'scrollbar_selected_insensitive_xsize', 'scrollbar_selected_insensitive_xysize', 'scrollbar_selected_insensitive_yalign', 'scrollbar_selected_insensitive_yanchor', 'scrollbar_selected_insensitive_ycenter', 'scrollbar_selected_insensitive_yfill', 'scrollbar_selected_insensitive_ymaximum', 'scrollbar_selected_insensitive_yoffset', 'scrollbar_selected_insensitive_ypos', 'scrollbar_selected_insensitive_ysize', 'scrollbar_selected_keyboard_focus', 'scrollbar_selected_left_bar', 'scrollbar_selected_left_gutter', 'scrollbar_selected_maximum', 'scrollbar_selected_mouse', 'scrollbar_selected_offset', 'scrollbar_selected_pos', 'scrollbar_selected_right_bar', 'scrollbar_selected_right_gutter', 'scrollbar_selected_thumb', 'scrollbar_selected_thumb_offset', 'scrollbar_selected_thumb_shadow', 'scrollbar_selected_tooltip', 'scrollbar_selected_top_bar', 'scrollbar_selected_top_gutter', 'scrollbar_selected_unscrollable', 'scrollbar_selected_xalign', 'scrollbar_selected_xanchor', 'scrollbar_selected_xcenter', 'scrollbar_selected_xfill', 'scrollbar_selected_xmaximum', 'scrollbar_selected_xoffset', 'scrollbar_selected_xpos', 'scrollbar_selected_xsize', 'scrollbar_selected_xysize', 'scrollbar_selected_yalign', 'scrollbar_selected_yanchor', 'scrollbar_selected_ycenter', 'scrollbar_selected_yfill', 'scrollbar_selected_ymaximum', 'scrollbar_selected_yoffset', 'scrollbar_selected_ypos', 'scrollbar_selected_ysize', 'scrollbar_thumb', 'scrollbar_thumb_offset', 'scrollbar_thumb_shadow', 'scrollbar_tooltip', 'scrollbar_top_bar', 'scrollbar_top_gutter', 'scrollbar_unscrollable', 'scrollbar_xalign', 'scrollbar_xanchor', 'scrollbar_xcenter', 'scrollbar_xfill', 'scrollbar_xmaximum', 'scrollbar_xoffset', 'scrollbar_xpos', 'scrollbar_xsize', 'scrollbar_xysize', 'scrollbar_yalign', 'scrollbar_yanchor', 'scrollbar_ycenter', 'scrollbar_yfill', 'scrollbar_ymaximum', 'scrollbar_yoffset', 'scrollbar_ypos', 'scrollbar_ysize', 'scrollbars', 'selected', 'selected_activate_additive', 'selected_activate_adjust_spacing', 'selected_activate_align', 'selected_activate_alignaround', 'selected_activate_alpha', 'selected_activate_alt', 'selected_activate_anchor', 'selected_activate_angle', 'selected_activate_antialias', 'selected_activate_area', 'selected_activate_around', 'selected_activate_background', 'selected_activate_bar_invert', 'selected_activate_bar_resizing', 'selected_activate_bar_vertical', 'selected_activate_base_bar', 'selected_activate_black_color', 'selected_activate_bold', 'selected_activate_bottom_bar', 'selected_activate_bottom_gutter', 'selected_activate_bottom_margin', 'selected_activate_bottom_padding', 'selected_activate_box_layout', 'selected_activate_box_reverse', 'selected_activate_box_wrap', 'selected_activate_box_wrap_spacing', 'selected_activate_caret', 'selected_activate_child', 'selected_activate_clipping', 'selected_activate_color', 'selected_activate_corner1', 'selected_activate_corner2', 'selected_activate_crop', 'selected_activate_crop_relative', 'selected_activate_debug', 'selected_activate_delay', 'selected_activate_drop_shadow', 'selected_activate_drop_shadow_color', 'selected_activate_events', 'selected_activate_first_indent', 'selected_activate_first_spacing', 'selected_activate_fit_first', 'selected_activate_focus_mask', 'selected_activate_font', 'selected_activate_foreground', 'selected_activate_hinting', 'selected_activate_hyperlink_functions', 'selected_activate_italic', 'selected_activate_justify', 'selected_activate_kerning', 'selected_activate_key_events', 'selected_activate_keyboard_focus', 'selected_activate_language', 'selected_activate_layout', 'selected_activate_left_bar', 'selected_activate_left_gutter', 'selected_activate_left_margin', 'selected_activate_left_padding', 'selected_activate_line_leading', 'selected_activate_line_spacing', 'selected_activate_margin', 'selected_activate_maximum', 'selected_activate_maxsize', 'selected_activate_min_width', 'selected_activate_minimum', 'selected_activate_minwidth', 'selected_activate_mouse', 'selected_activate_nearest', 'selected_activate_newline_indent', 'selected_activate_offset', 'selected_activate_order_reverse', 'selected_activate_outline_scaling', 'selected_activate_outlines', 'selected_activate_padding', 'selected_activate_pos', 'selected_activate_radius', 'selected_activate_rest_indent', 'selected_activate_right_bar', 'selected_activate_right_gutter', 'selected_activate_right_margin', 'selected_activate_right_padding', 'selected_activate_rotate', 'selected_activate_rotate_pad', 'selected_activate_ruby_style', 'selected_activate_size', 'selected_activate_size_group', 'selected_activate_slow_abortable', 'selected_activate_slow_cps', 'selected_activate_slow_cps_multiplier', 'selected_activate_sound', 'selected_activate_spacing', 'selected_activate_strikethrough', 'selected_activate_subpixel', 'selected_activate_text_align', 'selected_activate_text_y_fudge', 'selected_activate_thumb', 'selected_activate_thumb_offset', 'selected_activate_thumb_shadow', 'selected_activate_tooltip', 'selected_activate_top_bar', 'selected_activate_top_gutter', 'selected_activate_top_margin', 'selected_activate_top_padding', 'selected_activate_transform_anchor', 'selected_activate_underline', 'selected_activate_unscrollable', 'selected_activate_vertical', 'selected_activate_xalign', 'selected_activate_xanchor', 'selected_activate_xanchoraround', 'selected_activate_xaround', 'selected_activate_xcenter', 'selected_activate_xfill', 'selected_activate_xfit', 'selected_activate_xmargin', 'selected_activate_xmaximum', 'selected_activate_xminimum', 'selected_activate_xoffset', 'selected_activate_xpadding', 'selected_activate_xpan', 'selected_activate_xpos', 'selected_activate_xsize', 'selected_activate_xspacing', 'selected_activate_xtile', 'selected_activate_xysize', 'selected_activate_xzoom', 'selected_activate_yalign', 'selected_activate_yanchor', 'selected_activate_yanchoraround', 'selected_activate_yaround', 'selected_activate_ycenter', 'selected_activate_yfill', 'selected_activate_yfit', 'selected_activate_ymargin', 'selected_activate_ymaximum', 'selected_activate_yminimum', 'selected_activate_yoffset', 'selected_activate_ypadding', 'selected_activate_ypan', 'selected_activate_ypos', 'selected_activate_ysize', 'selected_activate_yspacing', 'selected_activate_ytile', 'selected_activate_yzoom', 'selected_activate_zoom', 'selected_additive', 'selected_adjust_spacing', 'selected_align', 'selected_alignaround', 'selected_alpha', 'selected_alt', 'selected_anchor', 'selected_angle', 'selected_antialias', 'selected_area', 'selected_around', 'selected_background', 'selected_bar_invert', 'selected_bar_resizing', 'selected_bar_vertical', 'selected_base_bar', 'selected_black_color', 'selected_bold', 'selected_bottom_bar', 'selected_bottom_gutter', 'selected_bottom_margin', 'selected_bottom_padding', 'selected_box_layout', 'selected_box_reverse', 'selected_box_wrap', 'selected_box_wrap_spacing', 'selected_caret', 'selected_child', 'selected_clipping', 'selected_color', 'selected_corner1', 'selected_corner2', 'selected_crop', 'selected_crop_relative', 'selected_debug', 'selected_delay', 'selected_drop_shadow', 'selected_drop_shadow_color', 'selected_events', 'selected_first_indent', 'selected_first_spacing', 'selected_fit_first', 'selected_focus_mask', 'selected_font', 'selected_foreground', 'selected_hinting', 'selected_hover', 'selected_hover_additive', 'selected_hover_adjust_spacing', 'selected_hover_align', 'selected_hover_alignaround', 'selected_hover_alpha', 'selected_hover_alt', 'selected_hover_anchor', 'selected_hover_angle', 'selected_hover_antialias', 'selected_hover_area', 'selected_hover_around', 'selected_hover_background', 'selected_hover_bar_invert', 'selected_hover_bar_resizing', 'selected_hover_bar_vertical', 'selected_hover_base_bar', 'selected_hover_black_color', 'selected_hover_bold', 'selected_hover_bottom_bar', 'selected_hover_bottom_gutter', 'selected_hover_bottom_margin', 'selected_hover_bottom_padding', 'selected_hover_box_layout', 'selected_hover_box_reverse', 'selected_hover_box_wrap', 'selected_hover_box_wrap_spacing', 'selected_hover_caret', 'selected_hover_child', 'selected_hover_clipping', 'selected_hover_color', 'selected_hover_corner1', 'selected_hover_corner2', 'selected_hover_crop', 'selected_hover_crop_relative', 'selected_hover_debug', 'selected_hover_delay', 'selected_hover_drop_shadow', 'selected_hover_drop_shadow_color', 'selected_hover_events', 'selected_hover_first_indent', 'selected_hover_first_spacing', 'selected_hover_fit_first', 'selected_hover_focus_mask', 'selected_hover_font', 'selected_hover_foreground', 'selected_hover_hinting', 'selected_hover_hyperlink_functions', 'selected_hover_italic', 'selected_hover_justify', 'selected_hover_kerning', 'selected_hover_key_events', 'selected_hover_keyboard_focus', 'selected_hover_language', 'selected_hover_layout', 'selected_hover_left_bar', 'selected_hover_left_gutter', 'selected_hover_left_margin', 'selected_hover_left_padding', 'selected_hover_line_leading', 'selected_hover_line_spacing', 'selected_hover_margin', 'selected_hover_maximum', 'selected_hover_maxsize', 'selected_hover_min_width', 'selected_hover_minimum', 'selected_hover_minwidth', 'selected_hover_mouse', 'selected_hover_nearest', 'selected_hover_newline_indent', 'selected_hover_offset', 'selected_hover_order_reverse', 'selected_hover_outline_scaling', 'selected_hover_outlines', 'selected_hover_padding', 'selected_hover_pos', 'selected_hover_radius', 'selected_hover_rest_indent', 'selected_hover_right_bar', 'selected_hover_right_gutter', 'selected_hover_right_margin', 'selected_hover_right_padding', 'selected_hover_rotate', 'selected_hover_rotate_pad', 'selected_hover_ruby_style', 'selected_hover_size', 'selected_hover_size_group', 'selected_hover_slow_abortable', 'selected_hover_slow_cps', 'selected_hover_slow_cps_multiplier', 'selected_hover_sound', 'selected_hover_spacing', 'selected_hover_strikethrough', 'selected_hover_subpixel', 'selected_hover_text_align', 'selected_hover_text_y_fudge', 'selected_hover_thumb', 'selected_hover_thumb_offset', 'selected_hover_thumb_shadow', 'selected_hover_tooltip', 'selected_hover_top_bar', 'selected_hover_top_gutter', 'selected_hover_top_margin', 'selected_hover_top_padding', 'selected_hover_transform_anchor', 'selected_hover_underline', 'selected_hover_unscrollable', 'selected_hover_vertical', 'selected_hover_xalign', 'selected_hover_xanchor', 'selected_hover_xanchoraround', 'selected_hover_xaround', 'selected_hover_xcenter', 'selected_hover_xfill', 'selected_hover_xfit', 'selected_hover_xmargin', 'selected_hover_xmaximum', 'selected_hover_xminimum', 'selected_hover_xoffset', 'selected_hover_xpadding', 'selected_hover_xpan', 'selected_hover_xpos', 'selected_hover_xsize', 'selected_hover_xspacing', 'selected_hover_xtile', 'selected_hover_xysize', 'selected_hover_xzoom', 'selected_hover_yalign', 'selected_hover_yanchor', 'selected_hover_yanchoraround', 'selected_hover_yaround', 'selected_hover_ycenter', 'selected_hover_yfill', 'selected_hover_yfit', 'selected_hover_ymargin', 'selected_hover_ymaximum', 'selected_hover_yminimum', 'selected_hover_yoffset', 'selected_hover_ypadding', 'selected_hover_ypan', 'selected_hover_ypos', 'selected_hover_ysize', 'selected_hover_yspacing', 'selected_hover_ytile', 'selected_hover_yzoom', 'selected_hover_zoom', 'selected_hyperlink_functions', 'selected_idle', 'selected_idle_additive', 'selected_idle_adjust_spacing', 'selected_idle_align', 'selected_idle_alignaround', 'selected_idle_alpha', 'selected_idle_alt', 'selected_idle_anchor', 'selected_idle_angle', 'selected_idle_antialias', 'selected_idle_area', 'selected_idle_around', 'selected_idle_background', 'selected_idle_bar_invert', 'selected_idle_bar_resizing', 'selected_idle_bar_vertical', 'selected_idle_base_bar', 'selected_idle_black_color', 'selected_idle_bold', 'selected_idle_bottom_bar', 'selected_idle_bottom_gutter', 'selected_idle_bottom_margin', 'selected_idle_bottom_padding', 'selected_idle_box_layout', 'selected_idle_box_reverse', 'selected_idle_box_wrap', 'selected_idle_box_wrap_spacing', 'selected_idle_caret', 'selected_idle_child', 'selected_idle_clipping', 'selected_idle_color', 'selected_idle_corner1', 'selected_idle_corner2', 'selected_idle_crop', 'selected_idle_crop_relative', 'selected_idle_debug', 'selected_idle_delay', 'selected_idle_drop_shadow', 'selected_idle_drop_shadow_color', 'selected_idle_events', 'selected_idle_first_indent', 'selected_idle_first_spacing', 'selected_idle_fit_first', 'selected_idle_focus_mask', 'selected_idle_font', 'selected_idle_foreground', 'selected_idle_hinting', 'selected_idle_hyperlink_functions', 'selected_idle_italic', 'selected_idle_justify', 'selected_idle_kerning', 'selected_idle_key_events', 'selected_idle_keyboard_focus', 'selected_idle_language', 'selected_idle_layout', 'selected_idle_left_bar', 'selected_idle_left_gutter', 'selected_idle_left_margin', 'selected_idle_left_padding', 'selected_idle_line_leading', 'selected_idle_line_spacing', 'selected_idle_margin', 'selected_idle_maximum', 'selected_idle_maxsize', 'selected_idle_min_width', 'selected_idle_minimum', 'selected_idle_minwidth', 'selected_idle_mouse', 'selected_idle_nearest', 'selected_idle_newline_indent', 'selected_idle_offset', 'selected_idle_order_reverse', 'selected_idle_outline_scaling', 'selected_idle_outlines', 'selected_idle_padding', 'selected_idle_pos', 'selected_idle_radius', 'selected_idle_rest_indent', 'selected_idle_right_bar', 'selected_idle_right_gutter', 'selected_idle_right_margin', 'selected_idle_right_padding', 'selected_idle_rotate', 'selected_idle_rotate_pad', 'selected_idle_ruby_style', 'selected_idle_size', 'selected_idle_size_group', 'selected_idle_slow_abortable', 'selected_idle_slow_cps', 'selected_idle_slow_cps_multiplier', 'selected_idle_sound', 'selected_idle_spacing', 'selected_idle_strikethrough', 'selected_idle_subpixel', 'selected_idle_text_align', 'selected_idle_text_y_fudge', 'selected_idle_thumb', 'selected_idle_thumb_offset', 'selected_idle_thumb_shadow', 'selected_idle_tooltip', 'selected_idle_top_bar', 'selected_idle_top_gutter', 'selected_idle_top_margin', 'selected_idle_top_padding', 'selected_idle_transform_anchor', 'selected_idle_underline', 'selected_idle_unscrollable', 'selected_idle_vertical', 'selected_idle_xalign', 'selected_idle_xanchor', 'selected_idle_xanchoraround', 'selected_idle_xaround', 'selected_idle_xcenter', 'selected_idle_xfill', 'selected_idle_xfit', 'selected_idle_xmargin', 'selected_idle_xmaximum', 'selected_idle_xminimum', 'selected_idle_xoffset', 'selected_idle_xpadding', 'selected_idle_xpan', 'selected_idle_xpos', 'selected_idle_xsize', 'selected_idle_xspacing', 'selected_idle_xtile', 'selected_idle_xysize', 'selected_idle_xzoom', 'selected_idle_yalign', 'selected_idle_yanchor', 'selected_idle_yanchoraround', 'selected_idle_yaround', 'selected_idle_ycenter', 'selected_idle_yfill', 'selected_idle_yfit', 'selected_idle_ymargin', 'selected_idle_ymaximum', 'selected_idle_yminimum', 'selected_idle_yoffset', 'selected_idle_ypadding', 'selected_idle_ypan', 'selected_idle_ypos', 'selected_idle_ysize', 'selected_idle_yspacing', 'selected_idle_ytile', 'selected_idle_yzoom', 'selected_idle_zoom', 'selected_insensitive', 'selected_insensitive_additive', 'selected_insensitive_adjust_spacing', 'selected_insensitive_align', 'selected_insensitive_alignaround', 'selected_insensitive_alpha', 'selected_insensitive_alt', 'selected_insensitive_anchor', 'selected_insensitive_angle', 'selected_insensitive_antialias', 'selected_insensitive_area', 'selected_insensitive_around', 'selected_insensitive_background', 'selected_insensitive_bar_invert', 'selected_insensitive_bar_resizing', 'selected_insensitive_bar_vertical', 'selected_insensitive_base_bar', 'selected_insensitive_black_color', 'selected_insensitive_bold', 'selected_insensitive_bottom_bar', 'selected_insensitive_bottom_gutter', 'selected_insensitive_bottom_margin', 'selected_insensitive_bottom_padding', 'selected_insensitive_box_layout', 'selected_insensitive_box_reverse', 'selected_insensitive_box_wrap', 'selected_insensitive_box_wrap_spacing', 'selected_insensitive_caret', 'selected_insensitive_child', 'selected_insensitive_clipping', 'selected_insensitive_color', 'selected_insensitive_corner1', 'selected_insensitive_corner2', 'selected_insensitive_crop', 'selected_insensitive_crop_relative', 'selected_insensitive_debug', 'selected_insensitive_delay', 'selected_insensitive_drop_shadow', 'selected_insensitive_drop_shadow_color', 'selected_insensitive_events', 'selected_insensitive_first_indent', 'selected_insensitive_first_spacing', 'selected_insensitive_fit_first', 'selected_insensitive_focus_mask', 'selected_insensitive_font', 'selected_insensitive_foreground', 'selected_insensitive_hinting', 'selected_insensitive_hyperlink_functions', 'selected_insensitive_italic', 'selected_insensitive_justify', 'selected_insensitive_kerning', 'selected_insensitive_key_events', 'selected_insensitive_keyboard_focus', 'selected_insensitive_language', 'selected_insensitive_layout', 'selected_insensitive_left_bar', 'selected_insensitive_left_gutter', 'selected_insensitive_left_margin', 'selected_insensitive_left_padding', 'selected_insensitive_line_leading', 'selected_insensitive_line_spacing', 'selected_insensitive_margin', 'selected_insensitive_maximum', 'selected_insensitive_maxsize', 'selected_insensitive_min_width', 'selected_insensitive_minimum', 'selected_insensitive_minwidth', 'selected_insensitive_mouse', 'selected_insensitive_nearest', 'selected_insensitive_newline_indent', 'selected_insensitive_offset', 'selected_insensitive_order_reverse', 'selected_insensitive_outline_scaling', 'selected_insensitive_outlines', 'selected_insensitive_padding', 'selected_insensitive_pos', 'selected_insensitive_radius', 'selected_insensitive_rest_indent', 'selected_insensitive_right_bar', 'selected_insensitive_right_gutter', 'selected_insensitive_right_margin', 'selected_insensitive_right_padding', 'selected_insensitive_rotate', 'selected_insensitive_rotate_pad', 'selected_insensitive_ruby_style', 'selected_insensitive_size', 'selected_insensitive_size_group', 'selected_insensitive_slow_abortable', 'selected_insensitive_slow_cps', 'selected_insensitive_slow_cps_multiplier', 'selected_insensitive_sound', 'selected_insensitive_spacing', 'selected_insensitive_strikethrough', 'selected_insensitive_subpixel', 'selected_insensitive_text_align', 'selected_insensitive_text_y_fudge', 'selected_insensitive_thumb', 'selected_insensitive_thumb_offset', 'selected_insensitive_thumb_shadow', 'selected_insensitive_tooltip', 'selected_insensitive_top_bar', 'selected_insensitive_top_gutter', 'selected_insensitive_top_margin', 'selected_insensitive_top_padding', 'selected_insensitive_transform_anchor', 'selected_insensitive_underline', 'selected_insensitive_unscrollable', 'selected_insensitive_vertical', 'selected_insensitive_xalign', 'selected_insensitive_xanchor', 'selected_insensitive_xanchoraround', 'selected_insensitive_xaround', 'selected_insensitive_xcenter', 'selected_insensitive_xfill', 'selected_insensitive_xfit', 'selected_insensitive_xmargin', 'selected_insensitive_xmaximum', 'selected_insensitive_xminimum', 'selected_insensitive_xoffset', 'selected_insensitive_xpadding', 'selected_insensitive_xpan', 'selected_insensitive_xpos', 'selected_insensitive_xsize', 'selected_insensitive_xspacing', 'selected_insensitive_xtile', 'selected_insensitive_xysize', 'selected_insensitive_xzoom', 'selected_insensitive_yalign', 'selected_insensitive_yanchor', 'selected_insensitive_yanchoraround', 'selected_insensitive_yaround', 'selected_insensitive_ycenter', 'selected_insensitive_yfill', 'selected_insensitive_yfit', 'selected_insensitive_ymargin', 'selected_insensitive_ymaximum', 'selected_insensitive_yminimum', 'selected_insensitive_yoffset', 'selected_insensitive_ypadding', 'selected_insensitive_ypan', 'selected_insensitive_ypos', 'selected_insensitive_ysize', 'selected_insensitive_yspacing', 'selected_insensitive_ytile', 'selected_insensitive_yzoom', 'selected_insensitive_zoom', 'selected_italic', 'selected_justify', 'selected_kerning', 'selected_key_events', 'selected_keyboard_focus', 'selected_language', 'selected_layout', 'selected_left_bar', 'selected_left_gutter', 'selected_left_margin', 'selected_left_padding', 'selected_line_leading', 'selected_line_spacing', 'selected_margin', 'selected_maximum', 'selected_maxsize', 'selected_min_width', 'selected_minimum', 'selected_minwidth', 'selected_mouse', 'selected_nearest', 'selected_newline_indent', 'selected_offset', 'selected_order_reverse', 'selected_outline_scaling', 'selected_outlines', 'selected_padding', 'selected_pos', 'selected_radius', 'selected_rest_indent', 'selected_right_bar', 'selected_right_gutter', 'selected_right_margin', 'selected_right_padding', 'selected_rotate', 'selected_rotate_pad', 'selected_ruby_style', 'selected_size', 'selected_size_group', 'selected_slow_abortable', 'selected_slow_cps', 'selected_slow_cps_multiplier', 'selected_sound', 'selected_spacing', 'selected_strikethrough', 'selected_subpixel', 'selected_text_align', 'selected_text_y_fudge', 'selected_thumb', 'selected_thumb_offset', 'selected_thumb_shadow', 'selected_tooltip', 'selected_top_bar', 'selected_top_gutter', 'selected_top_margin', 'selected_top_padding', 'selected_transform_anchor', 'selected_underline', 'selected_unscrollable', 'selected_vertical', 'selected_xalign', 'selected_xanchor', 'selected_xanchoraround', 'selected_xaround', 'selected_xcenter', 'selected_xfill', 'selected_xfit', 'selected_xmargin', 'selected_xmaximum', 'selected_xminimum', 'selected_xoffset', 'selected_xpadding', 'selected_xpan', 'selected_xpos', 'selected_xsize', 'selected_xspacing', 'selected_xtile', 'selected_xysize', 'selected_xzoom', 'selected_yalign', 'selected_yanchor', 'selected_yanchoraround', 'selected_yaround', 'selected_ycenter', 'selected_yfill', 'selected_yfit', 'selected_ymargin', 'selected_ymaximum', 'selected_yminimum', 'selected_yoffset', 'selected_ypadding', 'selected_ypan', 'selected_ypos', 'selected_ysize', 'selected_yspacing', 'selected_ytile', 'selected_yzoom', 'selected_zoom', 'sensitive', 'side_activate_align', 'side_activate_alt', 'side_activate_anchor', 'side_activate_area', 'side_activate_clipping', 'side_activate_debug', 'side_activate_maximum', 'side_activate_offset', 'side_activate_pos', 'side_activate_spacing', 'side_activate_tooltip', 'side_activate_xalign', 'side_activate_xanchor', 'side_activate_xcenter', 'side_activate_xfill', 'side_activate_xmaximum', 'side_activate_xoffset', 'side_activate_xpos', 'side_activate_xsize', 'side_activate_xysize', 'side_activate_yalign', 'side_activate_yanchor', 'side_activate_ycenter', 'side_activate_yfill', 'side_activate_ymaximum', 'side_activate_yoffset', 'side_activate_ypos', 'side_activate_ysize', 'side_align', 'side_alt', 'side_anchor', 'side_area', 'side_clipping', 'side_debug', 'side_hover_align', 'side_hover_alt', 'side_hover_anchor', 'side_hover_area', 'side_hover_clipping', 'side_hover_debug', 'side_hover_maximum', 'side_hover_offset', 'side_hover_pos', 'side_hover_spacing', 'side_hover_tooltip', 'side_hover_xalign', 'side_hover_xanchor', 'side_hover_xcenter', 'side_hover_xfill', 'side_hover_xmaximum', 'side_hover_xoffset', 'side_hover_xpos', 'side_hover_xsize', 'side_hover_xysize', 'side_hover_yalign', 'side_hover_yanchor', 'side_hover_ycenter', 'side_hover_yfill', 'side_hover_ymaximum', 'side_hover_yoffset', 'side_hover_ypos', 'side_hover_ysize', 'side_idle_align', 'side_idle_alt', 'side_idle_anchor', 'side_idle_area', 'side_idle_clipping', 'side_idle_debug', 'side_idle_maximum', 'side_idle_offset', 'side_idle_pos', 'side_idle_spacing', 'side_idle_tooltip', 'side_idle_xalign', 'side_idle_xanchor', 'side_idle_xcenter', 'side_idle_xfill', 'side_idle_xmaximum', 'side_idle_xoffset', 'side_idle_xpos', 'side_idle_xsize', 'side_idle_xysize', 'side_idle_yalign', 'side_idle_yanchor', 'side_idle_ycenter', 'side_idle_yfill', 'side_idle_ymaximum', 'side_idle_yoffset', 'side_idle_ypos', 'side_idle_ysize', 'side_insensitive_align', 'side_insensitive_alt', 'side_insensitive_anchor', 'side_insensitive_area', 'side_insensitive_clipping', 'side_insensitive_debug', 'side_insensitive_maximum', 'side_insensitive_offset', 'side_insensitive_pos', 'side_insensitive_spacing', 'side_insensitive_tooltip', 'side_insensitive_xalign', 'side_insensitive_xanchor', 'side_insensitive_xcenter', 'side_insensitive_xfill', 'side_insensitive_xmaximum', 'side_insensitive_xoffset', 'side_insensitive_xpos', 'side_insensitive_xsize', 'side_insensitive_xysize', 'side_insensitive_yalign', 'side_insensitive_yanchor', 'side_insensitive_ycenter', 'side_insensitive_yfill', 'side_insensitive_ymaximum', 'side_insensitive_yoffset', 'side_insensitive_ypos', 'side_insensitive_ysize', 'side_maximum', 'side_offset', 'side_pos', 'side_selected_activate_align', 'side_selected_activate_alt', 'side_selected_activate_anchor', 'side_selected_activate_area', 'side_selected_activate_clipping', 'side_selected_activate_debug', 'side_selected_activate_maximum', 'side_selected_activate_offset', 'side_selected_activate_pos', 'side_selected_activate_spacing', 'side_selected_activate_tooltip', 'side_selected_activate_xalign', 'side_selected_activate_xanchor', 'side_selected_activate_xcenter', 'side_selected_activate_xfill', 'side_selected_activate_xmaximum', 'side_selected_activate_xoffset', 'side_selected_activate_xpos', 'side_selected_activate_xsize', 'side_selected_activate_xysize', 'side_selected_activate_yalign', 'side_selected_activate_yanchor', 'side_selected_activate_ycenter', 'side_selected_activate_yfill', 'side_selected_activate_ymaximum', 'side_selected_activate_yoffset', 'side_selected_activate_ypos', 'side_selected_activate_ysize', 'side_selected_align', 'side_selected_alt', 'side_selected_anchor', 'side_selected_area', 'side_selected_clipping', 'side_selected_debug', 'side_selected_hover_align', 'side_selected_hover_alt', 'side_selected_hover_anchor', 'side_selected_hover_area', 'side_selected_hover_clipping', 'side_selected_hover_debug', 'side_selected_hover_maximum', 'side_selected_hover_offset', 'side_selected_hover_pos', 'side_selected_hover_spacing', 'side_selected_hover_tooltip', 'side_selected_hover_xalign', 'side_selected_hover_xanchor', 'side_selected_hover_xcenter', 'side_selected_hover_xfill', 'side_selected_hover_xmaximum', 'side_selected_hover_xoffset', 'side_selected_hover_xpos', 'side_selected_hover_xsize', 'side_selected_hover_xysize', 'side_selected_hover_yalign', 'side_selected_hover_yanchor', 'side_selected_hover_ycenter', 'side_selected_hover_yfill', 'side_selected_hover_ymaximum', 'side_selected_hover_yoffset', 'side_selected_hover_ypos', 'side_selected_hover_ysize', 'side_selected_idle_align', 'side_selected_idle_alt', 'side_selected_idle_anchor', 'side_selected_idle_area', 'side_selected_idle_clipping', 'side_selected_idle_debug', 'side_selected_idle_maximum', 'side_selected_idle_offset', 'side_selected_idle_pos', 'side_selected_idle_spacing', 'side_selected_idle_tooltip', 'side_selected_idle_xalign', 'side_selected_idle_xanchor', 'side_selected_idle_xcenter', 'side_selected_idle_xfill', 'side_selected_idle_xmaximum', 'side_selected_idle_xoffset', 'side_selected_idle_xpos', 'side_selected_idle_xsize', 'side_selected_idle_xysize', 'side_selected_idle_yalign', 'side_selected_idle_yanchor', 'side_selected_idle_ycenter', 'side_selected_idle_yfill', 'side_selected_idle_ymaximum', 'side_selected_idle_yoffset', 'side_selected_idle_ypos', 'side_selected_idle_ysize', 'side_selected_insensitive_align', 'side_selected_insensitive_alt', 'side_selected_insensitive_anchor', 'side_selected_insensitive_area', 'side_selected_insensitive_clipping', 'side_selected_insensitive_debug', 'side_selected_insensitive_maximum', 'side_selected_insensitive_offset', 'side_selected_insensitive_pos', 'side_selected_insensitive_spacing', 'side_selected_insensitive_tooltip', 'side_selected_insensitive_xalign', 'side_selected_insensitive_xanchor', 'side_selected_insensitive_xcenter', 'side_selected_insensitive_xfill', 'side_selected_insensitive_xmaximum', 'side_selected_insensitive_xoffset', 'side_selected_insensitive_xpos', 'side_selected_insensitive_xsize', 'side_selected_insensitive_xysize', 'side_selected_insensitive_yalign', 'side_selected_insensitive_yanchor', 'side_selected_insensitive_ycenter', 'side_selected_insensitive_yfill', 'side_selected_insensitive_ymaximum', 'side_selected_insensitive_yoffset', 'side_selected_insensitive_ypos', 'side_selected_insensitive_ysize', 'side_selected_maximum', 'side_selected_offset', 'side_selected_pos', 'side_selected_spacing', 'side_selected_tooltip', 'side_selected_xalign', 'side_selected_xanchor', 'side_selected_xcenter', 'side_selected_xfill', 'side_selected_xmaximum', 'side_selected_xoffset', 'side_selected_xpos', 'side_selected_xsize', 'side_selected_xysize', 'side_selected_yalign', 'side_selected_yanchor', 'side_selected_ycenter', 'side_selected_yfill', 'side_selected_ymaximum', 'side_selected_yoffset', 'side_selected_ypos', 'side_selected_ysize', 'side_spacing', 'side_tooltip', 'side_xalign', 'side_xanchor', 'side_xcenter', 'side_xfill', 'side_xmaximum', 'side_xoffset', 'side_xpos', 'side_xsize', 'side_xysize', 'side_yalign', 'side_yanchor', 'side_ycenter', 'side_yfill', 'side_ymaximum', 'side_yoffset', 'side_ypos', 'side_ysize', 'size', 'size_group', 'slow', 'slow_abortable', 'slow_cps', 'slow_cps_multiplier', 'slow_done', 'spacing', 'strikethrough', 'style_group', 'style_prefix', 'style_suffix', 'subpixel', 'substitute', 'suffix', 'text_activate_adjust_spacing', 'text_activate_align', 'text_activate_alt', 'text_activate_anchor', 'text_activate_antialias', 'text_activate_area', 'text_activate_black_color', 'text_activate_bold', 'text_activate_clipping', 'text_activate_color', 'text_activate_debug', 'text_activate_drop_shadow', 'text_activate_drop_shadow_color', 'text_activate_first_indent', 'text_activate_font', 'text_activate_hinting', 'text_activate_hyperlink_functions', 'text_activate_italic', 'text_activate_justify', 'text_activate_kerning', 'text_activate_language', 'text_activate_layout', 'text_activate_line_leading', 'text_activate_line_spacing', 'text_activate_maximum', 'text_activate_min_width', 'text_activate_minimum', 'text_activate_minwidth', 'text_activate_newline_indent', 'text_activate_offset', 'text_activate_outline_scaling', 'text_activate_outlines', 'text_activate_pos', 'text_activate_rest_indent', 'text_activate_ruby_style', 'text_activate_size', 'text_activate_slow_abortable', 'text_activate_slow_cps', 'text_activate_slow_cps_multiplier', 'text_activate_strikethrough', 'text_activate_text_align', 'text_activate_text_y_fudge', 'text_activate_tooltip', 'text_activate_underline', 'text_activate_vertical', 'text_activate_xalign', 'text_activate_xanchor', 'text_activate_xcenter', 'text_activate_xfill', 'text_activate_xmaximum', 'text_activate_xminimum', 'text_activate_xoffset', 'text_activate_xpos', 'text_activate_xsize', 'text_activate_xysize', 'text_activate_yalign', 'text_activate_yanchor', 'text_activate_ycenter', 'text_activate_yfill', 'text_activate_ymaximum', 'text_activate_yminimum', 'text_activate_yoffset', 'text_activate_ypos', 'text_activate_ysize', 'text_adjust_spacing', 'text_align', 'text_alt', 'text_anchor', 'text_antialias', 'text_area', 'text_black_color', 'text_bold', 'text_clipping', 'text_color', 'text_debug', 'text_drop_shadow', 'text_drop_shadow_color', 'text_first_indent', 'text_font', 'text_hinting', 'text_hover_adjust_spacing', 'text_hover_align', 'text_hover_alt', 'text_hover_anchor', 'text_hover_antialias', 'text_hover_area', 'text_hover_black_color', 'text_hover_bold', 'text_hover_clipping', 'text_hover_color', 'text_hover_debug', 'text_hover_drop_shadow', 'text_hover_drop_shadow_color', 'text_hover_first_indent', 'text_hover_font', 'text_hover_hinting', 'text_hover_hyperlink_functions', 'text_hover_italic', 'text_hover_justify', 'text_hover_kerning', 'text_hover_language', 'text_hover_layout', 'text_hover_line_leading', 'text_hover_line_spacing', 'text_hover_maximum', 'text_hover_min_width', 'text_hover_minimum', 'text_hover_minwidth', 'text_hover_newline_indent', 'text_hover_offset', 'text_hover_outline_scaling', 'text_hover_outlines', 'text_hover_pos', 'text_hover_rest_indent', 'text_hover_ruby_style', 'text_hover_size', 'text_hover_slow_abortable', 'text_hover_slow_cps', 'text_hover_slow_cps_multiplier', 'text_hover_strikethrough', 'text_hover_text_align', 'text_hover_text_y_fudge', 'text_hover_tooltip', 'text_hover_underline', 'text_hover_vertical', 'text_hover_xalign', 'text_hover_xanchor', 'text_hover_xcenter', 'text_hover_xfill', 'text_hover_xmaximum', 'text_hover_xminimum', 'text_hover_xoffset', 'text_hover_xpos', 'text_hover_xsize', 'text_hover_xysize', 'text_hover_yalign', 'text_hover_yanchor', 'text_hover_ycenter', 'text_hover_yfill', 'text_hover_ymaximum', 'text_hover_yminimum', 'text_hover_yoffset', 'text_hover_ypos', 'text_hover_ysize', 'text_hyperlink_functions', 'text_idle_adjust_spacing', 'text_idle_align', 'text_idle_alt', 'text_idle_anchor', 'text_idle_antialias', 'text_idle_area', 'text_idle_black_color', 'text_idle_bold', 'text_idle_clipping', 'text_idle_color', 'text_idle_debug', 'text_idle_drop_shadow', 'text_idle_drop_shadow_color', 'text_idle_first_indent', 'text_idle_font', 'text_idle_hinting', 'text_idle_hyperlink_functions', 'text_idle_italic', 'text_idle_justify', 'text_idle_kerning', 'text_idle_language', 'text_idle_layout', 'text_idle_line_leading', 'text_idle_line_spacing', 'text_idle_maximum', 'text_idle_min_width', 'text_idle_minimum', 'text_idle_minwidth', 'text_idle_newline_indent', 'text_idle_offset', 'text_idle_outline_scaling', 'text_idle_outlines', 'text_idle_pos', 'text_idle_rest_indent', 'text_idle_ruby_style', 'text_idle_size', 'text_idle_slow_abortable', 'text_idle_slow_cps', 'text_idle_slow_cps_multiplier', 'text_idle_strikethrough', 'text_idle_text_align', 'text_idle_text_y_fudge', 'text_idle_tooltip', 'text_idle_underline', 'text_idle_vertical', 'text_idle_xalign', 'text_idle_xanchor', 'text_idle_xcenter', 'text_idle_xfill', 'text_idle_xmaximum', 'text_idle_xminimum', 'text_idle_xoffset', 'text_idle_xpos', 'text_idle_xsize', 'text_idle_xysize', 'text_idle_yalign', 'text_idle_yanchor', 'text_idle_ycenter', 'text_idle_yfill', 'text_idle_ymaximum', 'text_idle_yminimum', 'text_idle_yoffset', 'text_idle_ypos', 'text_idle_ysize', 'text_insensitive_adjust_spacing', 'text_insensitive_align', 'text_insensitive_alt', 'text_insensitive_anchor', 'text_insensitive_antialias', 'text_insensitive_area', 'text_insensitive_black_color', 'text_insensitive_bold', 'text_insensitive_clipping', 'text_insensitive_color', 'text_insensitive_debug', 'text_insensitive_drop_shadow', 'text_insensitive_drop_shadow_color', 'text_insensitive_first_indent', 'text_insensitive_font', 'text_insensitive_hinting', 'text_insensitive_hyperlink_functions', 'text_insensitive_italic', 'text_insensitive_justify', 'text_insensitive_kerning', 'text_insensitive_language', 'text_insensitive_layout', 'text_insensitive_line_leading', 'text_insensitive_line_spacing', 'text_insensitive_maximum', 'text_insensitive_min_width', 'text_insensitive_minimum', 'text_insensitive_minwidth', 'text_insensitive_newline_indent', 'text_insensitive_offset', 'text_insensitive_outline_scaling', 'text_insensitive_outlines', 'text_insensitive_pos', 'text_insensitive_rest_indent', 'text_insensitive_ruby_style', 'text_insensitive_size', 'text_insensitive_slow_abortable', 'text_insensitive_slow_cps', 'text_insensitive_slow_cps_multiplier', 'text_insensitive_strikethrough', 'text_insensitive_text_align', 'text_insensitive_text_y_fudge', 'text_insensitive_tooltip', 'text_insensitive_underline', 'text_insensitive_vertical', 'text_insensitive_xalign', 'text_insensitive_xanchor', 'text_insensitive_xcenter', 'text_insensitive_xfill', 'text_insensitive_xmaximum', 'text_insensitive_xminimum', 'text_insensitive_xoffset', 'text_insensitive_xpos', 'text_insensitive_xsize', 'text_insensitive_xysize', 'text_insensitive_yalign', 'text_insensitive_yanchor', 'text_insensitive_ycenter', 'text_insensitive_yfill', 'text_insensitive_ymaximum', 'text_insensitive_yminimum', 'text_insensitive_yoffset', 'text_insensitive_ypos', 'text_insensitive_ysize', 'text_italic', 'text_justify', 'text_kerning', 'text_language', 'text_layout', 'text_line_leading', 'text_line_spacing', 'text_maximum', 'text_min_width', 'text_minimum', 'text_minwidth', 'text_newline_indent', 'text_offset', 'text_outline_scaling', 'text_outlines', 'text_pos', 'text_rest_indent', 'text_ruby_style', 'text_selected_activate_adjust_spacing', 'text_selected_activate_align', 'text_selected_activate_alt', 'text_selected_activate_anchor', 'text_selected_activate_antialias', 'text_selected_activate_area', 'text_selected_activate_black_color', 'text_selected_activate_bold', 'text_selected_activate_clipping', 'text_selected_activate_color', 'text_selected_activate_debug', 'text_selected_activate_drop_shadow', 'text_selected_activate_drop_shadow_color', 'text_selected_activate_first_indent', 'text_selected_activate_font', 'text_selected_activate_hinting', 'text_selected_activate_hyperlink_functions', 'text_selected_activate_italic', 'text_selected_activate_justify', 'text_selected_activate_kerning', 'text_selected_activate_language', 'text_selected_activate_layout', 'text_selected_activate_line_leading', 'text_selected_activate_line_spacing', 'text_selected_activate_maximum', 'text_selected_activate_min_width', 'text_selected_activate_minimum', 'text_selected_activate_minwidth', 'text_selected_activate_newline_indent', 'text_selected_activate_offset', 'text_selected_activate_outline_scaling', 'text_selected_activate_outlines', 'text_selected_activate_pos', 'text_selected_activate_rest_indent', 'text_selected_activate_ruby_style', 'text_selected_activate_size', 'text_selected_activate_slow_abortable', 'text_selected_activate_slow_cps', 'text_selected_activate_slow_cps_multiplier', 'text_selected_activate_strikethrough', 'text_selected_activate_text_align', 'text_selected_activate_text_y_fudge', 'text_selected_activate_tooltip', 'text_selected_activate_underline', 'text_selected_activate_vertical', 'text_selected_activate_xalign', 'text_selected_activate_xanchor', 'text_selected_activate_xcenter', 'text_selected_activate_xfill', 'text_selected_activate_xmaximum', 'text_selected_activate_xminimum', 'text_selected_activate_xoffset', 'text_selected_activate_xpos', 'text_selected_activate_xsize', 'text_selected_activate_xysize', 'text_selected_activate_yalign', 'text_selected_activate_yanchor', 'text_selected_activate_ycenter', 'text_selected_activate_yfill', 'text_selected_activate_ymaximum', 'text_selected_activate_yminimum', 'text_selected_activate_yoffset', 'text_selected_activate_ypos', 'text_selected_activate_ysize', 'text_selected_adjust_spacing', 'text_selected_align', 'text_selected_alt', 'text_selected_anchor', 'text_selected_antialias', 'text_selected_area', 'text_selected_black_color', 'text_selected_bold', 'text_selected_clipping', 'text_selected_color', 'text_selected_debug', 'text_selected_drop_shadow', 'text_selected_drop_shadow_color', 'text_selected_first_indent', 'text_selected_font', 'text_selected_hinting', 'text_selected_hover_adjust_spacing', 'text_selected_hover_align', 'text_selected_hover_alt', 'text_selected_hover_anchor', 'text_selected_hover_antialias', 'text_selected_hover_area', 'text_selected_hover_black_color', 'text_selected_hover_bold', 'text_selected_hover_clipping', 'text_selected_hover_color', 'text_selected_hover_debug', 'text_selected_hover_drop_shadow', 'text_selected_hover_drop_shadow_color', 'text_selected_hover_first_indent', 'text_selected_hover_font', 'text_selected_hover_hinting', 'text_selected_hover_hyperlink_functions', 'text_selected_hover_italic', 'text_selected_hover_justify', 'text_selected_hover_kerning', 'text_selected_hover_language', 'text_selected_hover_layout', 'text_selected_hover_line_leading', 'text_selected_hover_line_spacing', 'text_selected_hover_maximum', 'text_selected_hover_min_width', 'text_selected_hover_minimum', 'text_selected_hover_minwidth', 'text_selected_hover_newline_indent', 'text_selected_hover_offset', 'text_selected_hover_outline_scaling', 'text_selected_hover_outlines', 'text_selected_hover_pos', 'text_selected_hover_rest_indent', 'text_selected_hover_ruby_style', 'text_selected_hover_size', 'text_selected_hover_slow_abortable', 'text_selected_hover_slow_cps', 'text_selected_hover_slow_cps_multiplier', 'text_selected_hover_strikethrough', 'text_selected_hover_text_align', 'text_selected_hover_text_y_fudge', 'text_selected_hover_tooltip', 'text_selected_hover_underline', 'text_selected_hover_vertical', 'text_selected_hover_xalign', 'text_selected_hover_xanchor', 'text_selected_hover_xcenter', 'text_selected_hover_xfill', 'text_selected_hover_xmaximum', 'text_selected_hover_xminimum', 'text_selected_hover_xoffset', 'text_selected_hover_xpos', 'text_selected_hover_xsize', 'text_selected_hover_xysize', 'text_selected_hover_yalign', 'text_selected_hover_yanchor', 'text_selected_hover_ycenter', 'text_selected_hover_yfill', 'text_selected_hover_ymaximum', 'text_selected_hover_yminimum', 'text_selected_hover_yoffset', 'text_selected_hover_ypos', 'text_selected_hover_ysize', 'text_selected_hyperlink_functions', 'text_selected_idle_adjust_spacing', 'text_selected_idle_align', 'text_selected_idle_alt', 'text_selected_idle_anchor', 'text_selected_idle_antialias', 'text_selected_idle_area', 'text_selected_idle_black_color', 'text_selected_idle_bold', 'text_selected_idle_clipping', 'text_selected_idle_color', 'text_selected_idle_debug', 'text_selected_idle_drop_shadow', 'text_selected_idle_drop_shadow_color', 'text_selected_idle_first_indent', 'text_selected_idle_font', 'text_selected_idle_hinting', 'text_selected_idle_hyperlink_functions', 'text_selected_idle_italic', 'text_selected_idle_justify', 'text_selected_idle_kerning', 'text_selected_idle_language', 'text_selected_idle_layout', 'text_selected_idle_line_leading', 'text_selected_idle_line_spacing', 'text_selected_idle_maximum', 'text_selected_idle_min_width', 'text_selected_idle_minimum', 'text_selected_idle_minwidth', 'text_selected_idle_newline_indent', 'text_selected_idle_offset', 'text_selected_idle_outline_scaling', 'text_selected_idle_outlines', 'text_selected_idle_pos', 'text_selected_idle_rest_indent', 'text_selected_idle_ruby_style', 'text_selected_idle_size', 'text_selected_idle_slow_abortable', 'text_selected_idle_slow_cps', 'text_selected_idle_slow_cps_multiplier', 'text_selected_idle_strikethrough', 'text_selected_idle_text_align', 'text_selected_idle_text_y_fudge', 'text_selected_idle_tooltip', 'text_selected_idle_underline', 'text_selected_idle_vertical', 'text_selected_idle_xalign', 'text_selected_idle_xanchor', 'text_selected_idle_xcenter', 'text_selected_idle_xfill', 'text_selected_idle_xmaximum', 'text_selected_idle_xminimum', 'text_selected_idle_xoffset', 'text_selected_idle_xpos', 'text_selected_idle_xsize', 'text_selected_idle_xysize', 'text_selected_idle_yalign', 'text_selected_idle_yanchor', 'text_selected_idle_ycenter', 'text_selected_idle_yfill', 'text_selected_idle_ymaximum', 'text_selected_idle_yminimum', 'text_selected_idle_yoffset', 'text_selected_idle_ypos', 'text_selected_idle_ysize', 'text_selected_insensitive_adjust_spacing', 'text_selected_insensitive_align', 'text_selected_insensitive_alt', 'text_selected_insensitive_anchor', 'text_selected_insensitive_antialias', 'text_selected_insensitive_area', 'text_selected_insensitive_black_color', 'text_selected_insensitive_bold', 'text_selected_insensitive_clipping', 'text_selected_insensitive_color', 'text_selected_insensitive_debug', 'text_selected_insensitive_drop_shadow', 'text_selected_insensitive_drop_shadow_color', 'text_selected_insensitive_first_indent', 'text_selected_insensitive_font', 'text_selected_insensitive_hinting', 'text_selected_insensitive_hyperlink_functions', 'text_selected_insensitive_italic', 'text_selected_insensitive_justify', 'text_selected_insensitive_kerning', 'text_selected_insensitive_language', 'text_selected_insensitive_layout', 'text_selected_insensitive_line_leading', 'text_selected_insensitive_line_spacing', 'text_selected_insensitive_maximum', 'text_selected_insensitive_min_width', 'text_selected_insensitive_minimum', 'text_selected_insensitive_minwidth', 'text_selected_insensitive_newline_indent', 'text_selected_insensitive_offset', 'text_selected_insensitive_outline_scaling', 'text_selected_insensitive_outlines', 'text_selected_insensitive_pos', 'text_selected_insensitive_rest_indent', 'text_selected_insensitive_ruby_style', 'text_selected_insensitive_size', 'text_selected_insensitive_slow_abortable', 'text_selected_insensitive_slow_cps', 'text_selected_insensitive_slow_cps_multiplier', 'text_selected_insensitive_strikethrough', 'text_selected_insensitive_text_align', 'text_selected_insensitive_text_y_fudge', 'text_selected_insensitive_tooltip', 'text_selected_insensitive_underline', 'text_selected_insensitive_vertical', 'text_selected_insensitive_xalign', 'text_selected_insensitive_xanchor', 'text_selected_insensitive_xcenter', 'text_selected_insensitive_xfill', 'text_selected_insensitive_xmaximum', 'text_selected_insensitive_xminimum', 'text_selected_insensitive_xoffset', 'text_selected_insensitive_xpos', 'text_selected_insensitive_xsize', 'text_selected_insensitive_xysize', 'text_selected_insensitive_yalign', 'text_selected_insensitive_yanchor', 'text_selected_insensitive_ycenter', 'text_selected_insensitive_yfill', 'text_selected_insensitive_ymaximum', 'text_selected_insensitive_yminimum', 'text_selected_insensitive_yoffset', 'text_selected_insensitive_ypos', 'text_selected_insensitive_ysize', 'text_selected_italic', 'text_selected_justify', 'text_selected_kerning', 'text_selected_language', 'text_selected_layout', 'text_selected_line_leading', 'text_selected_line_spacing', 'text_selected_maximum', 'text_selected_min_width', 'text_selected_minimum', 'text_selected_minwidth', 'text_selected_newline_indent', 'text_selected_offset', 'text_selected_outline_scaling', 'text_selected_outlines', 'text_selected_pos', 'text_selected_rest_indent', 'text_selected_ruby_style', 'text_selected_size', 'text_selected_slow_abortable', 'text_selected_slow_cps', 'text_selected_slow_cps_multiplier', 'text_selected_strikethrough', 'text_selected_text_align', 'text_selected_text_y_fudge', 'text_selected_tooltip', 'text_selected_underline', 'text_selected_vertical', 'text_selected_xalign', 'text_selected_xanchor', 'text_selected_xcenter', 'text_selected_xfill', 'text_selected_xmaximum', 'text_selected_xminimum', 'text_selected_xoffset', 'text_selected_xpos', 'text_selected_xsize', 'text_selected_xysize', 'text_selected_yalign', 'text_selected_yanchor', 'text_selected_ycenter', 'text_selected_yfill', 'text_selected_ymaximum', 'text_selected_yminimum', 'text_selected_yoffset', 'text_selected_ypos', 'text_selected_ysize', 'text_size', 'text_slow_abortable', 'text_slow_cps', 'text_slow_cps_multiplier', 'text_strikethrough', 'text_style', 'text_text_align', 'text_text_y_fudge', 'text_tooltip', 'text_underline', 'text_vertical', 'text_xalign', 'text_xanchor', 'text_xcenter', 'text_xfill', 'text_xmaximum', 'text_xminimum', 'text_xoffset', 'text_xpos', 'text_xsize', 'text_xysize', 'text_y_fudge', 'text_yalign', 'text_yanchor', 'text_ycenter', 'text_yfill', 'text_ymaximum', 'text_yminimum', 'text_yoffset', 'text_ypos', 'text_ysize', 'thumb', 'thumb_offset', 'thumb_shadow', 'tooltip', 'top_bar', 'top_gutter', 'top_margin', 'top_padding', 'transform_anchor', 'transpose', 'underline', 'unhovered', 'unscrollable', 'value', 'variant', 'vertical', 'viewport_activate_align', 'viewport_activate_alt', 'viewport_activate_anchor', 'viewport_activate_area', 'viewport_activate_clipping', 'viewport_activate_debug', 'viewport_activate_maximum', 'viewport_activate_offset', 'viewport_activate_pos', 'viewport_activate_tooltip', 'viewport_activate_xalign', 'viewport_activate_xanchor', 'viewport_activate_xcenter', 'viewport_activate_xfill', 'viewport_activate_xmaximum', 'viewport_activate_xoffset', 'viewport_activate_xpos', 'viewport_activate_xsize', 'viewport_activate_xysize', 'viewport_activate_yalign', 'viewport_activate_yanchor', 'viewport_activate_ycenter', 'viewport_activate_yfill', 'viewport_activate_ymaximum', 'viewport_activate_yoffset', 'viewport_activate_ypos', 'viewport_activate_ysize', 'viewport_align', 'viewport_alt', 'viewport_anchor', 'viewport_area', 'viewport_clipping', 'viewport_debug', 'viewport_hover_align', 'viewport_hover_alt', 'viewport_hover_anchor', 'viewport_hover_area', 'viewport_hover_clipping', 'viewport_hover_debug', 'viewport_hover_maximum', 'viewport_hover_offset', 'viewport_hover_pos', 'viewport_hover_tooltip', 'viewport_hover_xalign', 'viewport_hover_xanchor', 'viewport_hover_xcenter', 'viewport_hover_xfill', 'viewport_hover_xmaximum', 'viewport_hover_xoffset', 'viewport_hover_xpos', 'viewport_hover_xsize', 'viewport_hover_xysize', 'viewport_hover_yalign', 'viewport_hover_yanchor', 'viewport_hover_ycenter', 'viewport_hover_yfill', 'viewport_hover_ymaximum', 'viewport_hover_yoffset', 'viewport_hover_ypos', 'viewport_hover_ysize', 'viewport_idle_align', 'viewport_idle_alt', 'viewport_idle_anchor', 'viewport_idle_area', 'viewport_idle_clipping', 'viewport_idle_debug', 'viewport_idle_maximum', 'viewport_idle_offset', 'viewport_idle_pos', 'viewport_idle_tooltip', 'viewport_idle_xalign', 'viewport_idle_xanchor', 'viewport_idle_xcenter', 'viewport_idle_xfill', 'viewport_idle_xmaximum', 'viewport_idle_xoffset', 'viewport_idle_xpos', 'viewport_idle_xsize', 'viewport_idle_xysize', 'viewport_idle_yalign', 'viewport_idle_yanchor', 'viewport_idle_ycenter', 'viewport_idle_yfill', 'viewport_idle_ymaximum', 'viewport_idle_yoffset', 'viewport_idle_ypos', 'viewport_idle_ysize', 'viewport_insensitive_align', 'viewport_insensitive_alt', 'viewport_insensitive_anchor', 'viewport_insensitive_area', 'viewport_insensitive_clipping', 'viewport_insensitive_debug', 'viewport_insensitive_maximum', 'viewport_insensitive_offset', 'viewport_insensitive_pos', 'viewport_insensitive_tooltip', 'viewport_insensitive_xalign', 'viewport_insensitive_xanchor', 'viewport_insensitive_xcenter', 'viewport_insensitive_xfill', 'viewport_insensitive_xmaximum', 'viewport_insensitive_xoffset', 'viewport_insensitive_xpos', 'viewport_insensitive_xsize', 'viewport_insensitive_xysize', 'viewport_insensitive_yalign', 'viewport_insensitive_yanchor', 'viewport_insensitive_ycenter', 'viewport_insensitive_yfill', 'viewport_insensitive_ymaximum', 'viewport_insensitive_yoffset', 'viewport_insensitive_ypos', 'viewport_insensitive_ysize', 'viewport_maximum', 'viewport_offset', 'viewport_pos', 'viewport_selected_activate_align', 'viewport_selected_activate_alt', 'viewport_selected_activate_anchor', 'viewport_selected_activate_area', 'viewport_selected_activate_clipping', 'viewport_selected_activate_debug', 'viewport_selected_activate_maximum', 'viewport_selected_activate_offset', 'viewport_selected_activate_pos', 'viewport_selected_activate_tooltip', 'viewport_selected_activate_xalign', 'viewport_selected_activate_xanchor', 'viewport_selected_activate_xcenter', 'viewport_selected_activate_xfill', 'viewport_selected_activate_xmaximum', 'viewport_selected_activate_xoffset', 'viewport_selected_activate_xpos', 'viewport_selected_activate_xsize', 'viewport_selected_activate_xysize', 'viewport_selected_activate_yalign', 'viewport_selected_activate_yanchor', 'viewport_selected_activate_ycenter', 'viewport_selected_activate_yfill', 'viewport_selected_activate_ymaximum', 'viewport_selected_activate_yoffset', 'viewport_selected_activate_ypos', 'viewport_selected_activate_ysize', 'viewport_selected_align', 'viewport_selected_alt', 'viewport_selected_anchor', 'viewport_selected_area', 'viewport_selected_clipping', 'viewport_selected_debug', 'viewport_selected_hover_align', 'viewport_selected_hover_alt', 'viewport_selected_hover_anchor', 'viewport_selected_hover_area', 'viewport_selected_hover_clipping', 'viewport_selected_hover_debug', 'viewport_selected_hover_maximum', 'viewport_selected_hover_offset', 'viewport_selected_hover_pos', 'viewport_selected_hover_tooltip', 'viewport_selected_hover_xalign', 'viewport_selected_hover_xanchor', 'viewport_selected_hover_xcenter', 'viewport_selected_hover_xfill', 'viewport_selected_hover_xmaximum', 'viewport_selected_hover_xoffset', 'viewport_selected_hover_xpos', 'viewport_selected_hover_xsize', 'viewport_selected_hover_xysize', 'viewport_selected_hover_yalign', 'viewport_selected_hover_yanchor', 'viewport_selected_hover_ycenter', 'viewport_selected_hover_yfill', 'viewport_selected_hover_ymaximum', 'viewport_selected_hover_yoffset', 'viewport_selected_hover_ypos', 'viewport_selected_hover_ysize', 'viewport_selected_idle_align', 'viewport_selected_idle_alt', 'viewport_selected_idle_anchor', 'viewport_selected_idle_area', 'viewport_selected_idle_clipping', 'viewport_selected_idle_debug', 'viewport_selected_idle_maximum', 'viewport_selected_idle_offset', 'viewport_selected_idle_pos', 'viewport_selected_idle_tooltip', 'viewport_selected_idle_xalign', 'viewport_selected_idle_xanchor', 'viewport_selected_idle_xcenter', 'viewport_selected_idle_xfill', 'viewport_selected_idle_xmaximum', 'viewport_selected_idle_xoffset', 'viewport_selected_idle_xpos', 'viewport_selected_idle_xsize', 'viewport_selected_idle_xysize', 'viewport_selected_idle_yalign', 'viewport_selected_idle_yanchor', 'viewport_selected_idle_ycenter', 'viewport_selected_idle_yfill', 'viewport_selected_idle_ymaximum', 'viewport_selected_idle_yoffset', 'viewport_selected_idle_ypos', 'viewport_selected_idle_ysize', 'viewport_selected_insensitive_align', 'viewport_selected_insensitive_alt', 'viewport_selected_insensitive_anchor', 'viewport_selected_insensitive_area', 'viewport_selected_insensitive_clipping', 'viewport_selected_insensitive_debug', 'viewport_selected_insensitive_maximum', 'viewport_selected_insensitive_offset', 'viewport_selected_insensitive_pos', 'viewport_selected_insensitive_tooltip', 'viewport_selected_insensitive_xalign', 'viewport_selected_insensitive_xanchor', 'viewport_selected_insensitive_xcenter', 'viewport_selected_insensitive_xfill', 'viewport_selected_insensitive_xmaximum', 'viewport_selected_insensitive_xoffset', 'viewport_selected_insensitive_xpos', 'viewport_selected_insensitive_xsize', 'viewport_selected_insensitive_xysize', 'viewport_selected_insensitive_yalign', 'viewport_selected_insensitive_yanchor', 'viewport_selected_insensitive_ycenter', 'viewport_selected_insensitive_yfill', 'viewport_selected_insensitive_ymaximum', 'viewport_selected_insensitive_yoffset', 'viewport_selected_insensitive_ypos', 'viewport_selected_insensitive_ysize', 'viewport_selected_maximum', 'viewport_selected_offset', 'viewport_selected_pos', 'viewport_selected_tooltip', 'viewport_selected_xalign', 'viewport_selected_xanchor', 'viewport_selected_xcenter', 'viewport_selected_xfill', 'viewport_selected_xmaximum', 'viewport_selected_xoffset', 'viewport_selected_xpos', 'viewport_selected_xsize', 'viewport_selected_xysize', 'viewport_selected_yalign', 'viewport_selected_yanchor', 'viewport_selected_ycenter', 'viewport_selected_yfill', 'viewport_selected_ymaximum', 'viewport_selected_yoffset', 'viewport_selected_ypos', 'viewport_selected_ysize', 'viewport_tooltip', 'viewport_xalign', 'viewport_xanchor', 'viewport_xcenter', 'viewport_xfill', 'viewport_xmaximum', 'viewport_xoffset', 'viewport_xpos', 'viewport_xsize', 'viewport_xysize', 'viewport_yalign', 'viewport_yanchor', 'viewport_ycenter', 'viewport_yfill', 'viewport_ymaximum', 'viewport_yoffset', 'viewport_ypos', 'viewport_ysize', 'vscrollbar_activate_align', 'vscrollbar_activate_alt', 'vscrollbar_activate_anchor', 'vscrollbar_activate_area', 'vscrollbar_activate_bar_invert', 'vscrollbar_activate_bar_resizing', 'vscrollbar_activate_bar_vertical', 'vscrollbar_activate_base_bar', 'vscrollbar_activate_bottom_bar', 'vscrollbar_activate_bottom_gutter', 'vscrollbar_activate_clipping', 'vscrollbar_activate_debug', 'vscrollbar_activate_keyboard_focus', 'vscrollbar_activate_left_bar', 'vscrollbar_activate_left_gutter', 'vscrollbar_activate_maximum', 'vscrollbar_activate_mouse', 'vscrollbar_activate_offset', 'vscrollbar_activate_pos', 'vscrollbar_activate_right_bar', 'vscrollbar_activate_right_gutter', 'vscrollbar_activate_thumb', 'vscrollbar_activate_thumb_offset', 'vscrollbar_activate_thumb_shadow', 'vscrollbar_activate_tooltip', 'vscrollbar_activate_top_bar', 'vscrollbar_activate_top_gutter', 'vscrollbar_activate_unscrollable', 'vscrollbar_activate_xalign', 'vscrollbar_activate_xanchor', 'vscrollbar_activate_xcenter', 'vscrollbar_activate_xfill', 'vscrollbar_activate_xmaximum', 'vscrollbar_activate_xoffset', 'vscrollbar_activate_xpos', 'vscrollbar_activate_xsize', 'vscrollbar_activate_xysize', 'vscrollbar_activate_yalign', 'vscrollbar_activate_yanchor', 'vscrollbar_activate_ycenter', 'vscrollbar_activate_yfill', 'vscrollbar_activate_ymaximum', 'vscrollbar_activate_yoffset', 'vscrollbar_activate_ypos', 'vscrollbar_activate_ysize', 'vscrollbar_align', 'vscrollbar_alt', 'vscrollbar_anchor', 'vscrollbar_area', 'vscrollbar_bar_invert', 'vscrollbar_bar_resizing', 'vscrollbar_bar_vertical', 'vscrollbar_base_bar', 'vscrollbar_bottom_bar', 'vscrollbar_bottom_gutter', 'vscrollbar_clipping', 'vscrollbar_debug', 'vscrollbar_hover_align', 'vscrollbar_hover_alt', 'vscrollbar_hover_anchor', 'vscrollbar_hover_area', 'vscrollbar_hover_bar_invert', 'vscrollbar_hover_bar_resizing', 'vscrollbar_hover_bar_vertical', 'vscrollbar_hover_base_bar', 'vscrollbar_hover_bottom_bar', 'vscrollbar_hover_bottom_gutter', 'vscrollbar_hover_clipping', 'vscrollbar_hover_debug', 'vscrollbar_hover_keyboard_focus', 'vscrollbar_hover_left_bar', 'vscrollbar_hover_left_gutter', 'vscrollbar_hover_maximum', 'vscrollbar_hover_mouse', 'vscrollbar_hover_offset', 'vscrollbar_hover_pos', 'vscrollbar_hover_right_bar', 'vscrollbar_hover_right_gutter', 'vscrollbar_hover_thumb', 'vscrollbar_hover_thumb_offset', 'vscrollbar_hover_thumb_shadow', 'vscrollbar_hover_tooltip', 'vscrollbar_hover_top_bar', 'vscrollbar_hover_top_gutter', 'vscrollbar_hover_unscrollable', 'vscrollbar_hover_xalign', 'vscrollbar_hover_xanchor', 'vscrollbar_hover_xcenter', 'vscrollbar_hover_xfill', 'vscrollbar_hover_xmaximum', 'vscrollbar_hover_xoffset', 'vscrollbar_hover_xpos', 'vscrollbar_hover_xsize', 'vscrollbar_hover_xysize', 'vscrollbar_hover_yalign', 'vscrollbar_hover_yanchor', 'vscrollbar_hover_ycenter', 'vscrollbar_hover_yfill', 'vscrollbar_hover_ymaximum', 'vscrollbar_hover_yoffset', 'vscrollbar_hover_ypos', 'vscrollbar_hover_ysize', 'vscrollbar_idle_align', 'vscrollbar_idle_alt', 'vscrollbar_idle_anchor', 'vscrollbar_idle_area', 'vscrollbar_idle_bar_invert', 'vscrollbar_idle_bar_resizing', 'vscrollbar_idle_bar_vertical', 'vscrollbar_idle_base_bar', 'vscrollbar_idle_bottom_bar', 'vscrollbar_idle_bottom_gutter', 'vscrollbar_idle_clipping', 'vscrollbar_idle_debug', 'vscrollbar_idle_keyboard_focus', 'vscrollbar_idle_left_bar', 'vscrollbar_idle_left_gutter', 'vscrollbar_idle_maximum', 'vscrollbar_idle_mouse', 'vscrollbar_idle_offset', 'vscrollbar_idle_pos', 'vscrollbar_idle_right_bar', 'vscrollbar_idle_right_gutter', 'vscrollbar_idle_thumb', 'vscrollbar_idle_thumb_offset', 'vscrollbar_idle_thumb_shadow', 'vscrollbar_idle_tooltip', 'vscrollbar_idle_top_bar', 'vscrollbar_idle_top_gutter', 'vscrollbar_idle_unscrollable', 'vscrollbar_idle_xalign', 'vscrollbar_idle_xanchor', 'vscrollbar_idle_xcenter', 'vscrollbar_idle_xfill', 'vscrollbar_idle_xmaximum', 'vscrollbar_idle_xoffset', 'vscrollbar_idle_xpos', 'vscrollbar_idle_xsize', 'vscrollbar_idle_xysize', 'vscrollbar_idle_yalign', 'vscrollbar_idle_yanchor', 'vscrollbar_idle_ycenter', 'vscrollbar_idle_yfill', 'vscrollbar_idle_ymaximum', 'vscrollbar_idle_yoffset', 'vscrollbar_idle_ypos', 'vscrollbar_idle_ysize', 'vscrollbar_insensitive_align', 'vscrollbar_insensitive_alt', 'vscrollbar_insensitive_anchor', 'vscrollbar_insensitive_area', 'vscrollbar_insensitive_bar_invert', 'vscrollbar_insensitive_bar_resizing', 'vscrollbar_insensitive_bar_vertical', 'vscrollbar_insensitive_base_bar', 'vscrollbar_insensitive_bottom_bar', 'vscrollbar_insensitive_bottom_gutter', 'vscrollbar_insensitive_clipping', 'vscrollbar_insensitive_debug', 'vscrollbar_insensitive_keyboard_focus', 'vscrollbar_insensitive_left_bar', 'vscrollbar_insensitive_left_gutter', 'vscrollbar_insensitive_maximum', 'vscrollbar_insensitive_mouse', 'vscrollbar_insensitive_offset', 'vscrollbar_insensitive_pos', 'vscrollbar_insensitive_right_bar', 'vscrollbar_insensitive_right_gutter', 'vscrollbar_insensitive_thumb', 'vscrollbar_insensitive_thumb_offset', 'vscrollbar_insensitive_thumb_shadow', 'vscrollbar_insensitive_tooltip', 'vscrollbar_insensitive_top_bar', 'vscrollbar_insensitive_top_gutter', 'vscrollbar_insensitive_unscrollable', 'vscrollbar_insensitive_xalign', 'vscrollbar_insensitive_xanchor', 'vscrollbar_insensitive_xcenter', 'vscrollbar_insensitive_xfill', 'vscrollbar_insensitive_xmaximum', 'vscrollbar_insensitive_xoffset', 'vscrollbar_insensitive_xpos', 'vscrollbar_insensitive_xsize', 'vscrollbar_insensitive_xysize', 'vscrollbar_insensitive_yalign', 'vscrollbar_insensitive_yanchor', 'vscrollbar_insensitive_ycenter', 'vscrollbar_insensitive_yfill', 'vscrollbar_insensitive_ymaximum', 'vscrollbar_insensitive_yoffset', 'vscrollbar_insensitive_ypos', 'vscrollbar_insensitive_ysize', 'vscrollbar_keyboard_focus', 'vscrollbar_left_bar', 'vscrollbar_left_gutter', 'vscrollbar_maximum', 'vscrollbar_mouse', 'vscrollbar_offset', 'vscrollbar_pos', 'vscrollbar_right_bar', 'vscrollbar_right_gutter', 'vscrollbar_selected_activate_align', 'vscrollbar_selected_activate_alt', 'vscrollbar_selected_activate_anchor', 'vscrollbar_selected_activate_area', 'vscrollbar_selected_activate_bar_invert', 'vscrollbar_selected_activate_bar_resizing', 'vscrollbar_selected_activate_bar_vertical', 'vscrollbar_selected_activate_base_bar', 'vscrollbar_selected_activate_bottom_bar', 'vscrollbar_selected_activate_bottom_gutter', 'vscrollbar_selected_activate_clipping', 'vscrollbar_selected_activate_debug', 'vscrollbar_selected_activate_keyboard_focus', 'vscrollbar_selected_activate_left_bar', 'vscrollbar_selected_activate_left_gutter', 'vscrollbar_selected_activate_maximum', 'vscrollbar_selected_activate_mouse', 'vscrollbar_selected_activate_offset', 'vscrollbar_selected_activate_pos', 'vscrollbar_selected_activate_right_bar', 'vscrollbar_selected_activate_right_gutter', 'vscrollbar_selected_activate_thumb', 'vscrollbar_selected_activate_thumb_offset', 'vscrollbar_selected_activate_thumb_shadow', 'vscrollbar_selected_activate_tooltip', 'vscrollbar_selected_activate_top_bar', 'vscrollbar_selected_activate_top_gutter', 'vscrollbar_selected_activate_unscrollable', 'vscrollbar_selected_activate_xalign', 'vscrollbar_selected_activate_xanchor', 'vscrollbar_selected_activate_xcenter', 'vscrollbar_selected_activate_xfill', 'vscrollbar_selected_activate_xmaximum', 'vscrollbar_selected_activate_xoffset', 'vscrollbar_selected_activate_xpos', 'vscrollbar_selected_activate_xsize', 'vscrollbar_selected_activate_xysize', 'vscrollbar_selected_activate_yalign', 'vscrollbar_selected_activate_yanchor', 'vscrollbar_selected_activate_ycenter', 'vscrollbar_selected_activate_yfill', 'vscrollbar_selected_activate_ymaximum', 'vscrollbar_selected_activate_yoffset', 'vscrollbar_selected_activate_ypos', 'vscrollbar_selected_activate_ysize', 'vscrollbar_selected_align', 'vscrollbar_selected_alt', 'vscrollbar_selected_anchor', 'vscrollbar_selected_area', 'vscrollbar_selected_bar_invert', 'vscrollbar_selected_bar_resizing', 'vscrollbar_selected_bar_vertical', 'vscrollbar_selected_base_bar', 'vscrollbar_selected_bottom_bar', 'vscrollbar_selected_bottom_gutter', 'vscrollbar_selected_clipping', 'vscrollbar_selected_debug', 'vscrollbar_selected_hover_align', 'vscrollbar_selected_hover_alt', 'vscrollbar_selected_hover_anchor', 'vscrollbar_selected_hover_area', 'vscrollbar_selected_hover_bar_invert', 'vscrollbar_selected_hover_bar_resizing', 'vscrollbar_selected_hover_bar_vertical', 'vscrollbar_selected_hover_base_bar', 'vscrollbar_selected_hover_bottom_bar', 'vscrollbar_selected_hover_bottom_gutter', 'vscrollbar_selected_hover_clipping', 'vscrollbar_selected_hover_debug', 'vscrollbar_selected_hover_keyboard_focus', 'vscrollbar_selected_hover_left_bar', 'vscrollbar_selected_hover_left_gutter', 'vscrollbar_selected_hover_maximum', 'vscrollbar_selected_hover_mouse', 'vscrollbar_selected_hover_offset', 'vscrollbar_selected_hover_pos', 'vscrollbar_selected_hover_right_bar', 'vscrollbar_selected_hover_right_gutter', 'vscrollbar_selected_hover_thumb', 'vscrollbar_selected_hover_thumb_offset', 'vscrollbar_selected_hover_thumb_shadow', 'vscrollbar_selected_hover_tooltip', 'vscrollbar_selected_hover_top_bar', 'vscrollbar_selected_hover_top_gutter', 'vscrollbar_selected_hover_unscrollable', 'vscrollbar_selected_hover_xalign', 'vscrollbar_selected_hover_xanchor', 'vscrollbar_selected_hover_xcenter', 'vscrollbar_selected_hover_xfill', 'vscrollbar_selected_hover_xmaximum', 'vscrollbar_selected_hover_xoffset', 'vscrollbar_selected_hover_xpos', 'vscrollbar_selected_hover_xsize', 'vscrollbar_selected_hover_xysize', 'vscrollbar_selected_hover_yalign', 'vscrollbar_selected_hover_yanchor', 'vscrollbar_selected_hover_ycenter', 'vscrollbar_selected_hover_yfill', 'vscrollbar_selected_hover_ymaximum', 'vscrollbar_selected_hover_yoffset', 'vscrollbar_selected_hover_ypos', 'vscrollbar_selected_hover_ysize', 'vscrollbar_selected_idle_align', 'vscrollbar_selected_idle_alt', 'vscrollbar_selected_idle_anchor', 'vscrollbar_selected_idle_area', 'vscrollbar_selected_idle_bar_invert', 'vscrollbar_selected_idle_bar_resizing', 'vscrollbar_selected_idle_bar_vertical', 'vscrollbar_selected_idle_base_bar', 'vscrollbar_selected_idle_bottom_bar', 'vscrollbar_selected_idle_bottom_gutter', 'vscrollbar_selected_idle_clipping', 'vscrollbar_selected_idle_debug', 'vscrollbar_selected_idle_keyboard_focus', 'vscrollbar_selected_idle_left_bar', 'vscrollbar_selected_idle_left_gutter', 'vscrollbar_selected_idle_maximum', 'vscrollbar_selected_idle_mouse', 'vscrollbar_selected_idle_offset', 'vscrollbar_selected_idle_pos', 'vscrollbar_selected_idle_right_bar', 'vscrollbar_selected_idle_right_gutter', 'vscrollbar_selected_idle_thumb', 'vscrollbar_selected_idle_thumb_offset', 'vscrollbar_selected_idle_thumb_shadow', 'vscrollbar_selected_idle_tooltip', 'vscrollbar_selected_idle_top_bar', 'vscrollbar_selected_idle_top_gutter', 'vscrollbar_selected_idle_unscrollable', 'vscrollbar_selected_idle_xalign', 'vscrollbar_selected_idle_xanchor', 'vscrollbar_selected_idle_xcenter', 'vscrollbar_selected_idle_xfill', 'vscrollbar_selected_idle_xmaximum', 'vscrollbar_selected_idle_xoffset', 'vscrollbar_selected_idle_xpos', 'vscrollbar_selected_idle_xsize', 'vscrollbar_selected_idle_xysize', 'vscrollbar_selected_idle_yalign', 'vscrollbar_selected_idle_yanchor', 'vscrollbar_selected_idle_ycenter', 'vscrollbar_selected_idle_yfill', 'vscrollbar_selected_idle_ymaximum', 'vscrollbar_selected_idle_yoffset', 'vscrollbar_selected_idle_ypos', 'vscrollbar_selected_idle_ysize', 'vscrollbar_selected_insensitive_align', 'vscrollbar_selected_insensitive_alt', 'vscrollbar_selected_insensitive_anchor', 'vscrollbar_selected_insensitive_area', 'vscrollbar_selected_insensitive_bar_invert', 'vscrollbar_selected_insensitive_bar_resizing', 'vscrollbar_selected_insensitive_bar_vertical', 'vscrollbar_selected_insensitive_base_bar', 'vscrollbar_selected_insensitive_bottom_bar', 'vscrollbar_selected_insensitive_bottom_gutter', 'vscrollbar_selected_insensitive_clipping', 'vscrollbar_selected_insensitive_debug', 'vscrollbar_selected_insensitive_keyboard_focus', 'vscrollbar_selected_insensitive_left_bar', 'vscrollbar_selected_insensitive_left_gutter', 'vscrollbar_selected_insensitive_maximum', 'vscrollbar_selected_insensitive_mouse', 'vscrollbar_selected_insensitive_offset', 'vscrollbar_selected_insensitive_pos', 'vscrollbar_selected_insensitive_right_bar', 'vscrollbar_selected_insensitive_right_gutter', 'vscrollbar_selected_insensitive_thumb', 'vscrollbar_selected_insensitive_thumb_offset', 'vscrollbar_selected_insensitive_thumb_shadow', 'vscrollbar_selected_insensitive_tooltip', 'vscrollbar_selected_insensitive_top_bar', 'vscrollbar_selected_insensitive_top_gutter', 'vscrollbar_selected_insensitive_unscrollable', 'vscrollbar_selected_insensitive_xalign', 'vscrollbar_selected_insensitive_xanchor', 'vscrollbar_selected_insensitive_xcenter', 'vscrollbar_selected_insensitive_xfill', 'vscrollbar_selected_insensitive_xmaximum', 'vscrollbar_selected_insensitive_xoffset', 'vscrollbar_selected_insensitive_xpos', 'vscrollbar_selected_insensitive_xsize', 'vscrollbar_selected_insensitive_xysize', 'vscrollbar_selected_insensitive_yalign', 'vscrollbar_selected_insensitive_yanchor', 'vscrollbar_selected_insensitive_ycenter', 'vscrollbar_selected_insensitive_yfill', 'vscrollbar_selected_insensitive_ymaximum', 'vscrollbar_selected_insensitive_yoffset', 'vscrollbar_selected_insensitive_ypos', 'vscrollbar_selected_insensitive_ysize', 'vscrollbar_selected_keyboard_focus', 'vscrollbar_selected_left_bar', 'vscrollbar_selected_left_gutter', 'vscrollbar_selected_maximum', 'vscrollbar_selected_mouse', 'vscrollbar_selected_offset', 'vscrollbar_selected_pos', 'vscrollbar_selected_right_bar', 'vscrollbar_selected_right_gutter', 'vscrollbar_selected_thumb', 'vscrollbar_selected_thumb_offset', 'vscrollbar_selected_thumb_shadow', 'vscrollbar_selected_tooltip', 'vscrollbar_selected_top_bar', 'vscrollbar_selected_top_gutter', 'vscrollbar_selected_unscrollable', 'vscrollbar_selected_xalign', 'vscrollbar_selected_xanchor', 'vscrollbar_selected_xcenter', 'vscrollbar_selected_xfill', 'vscrollbar_selected_xmaximum', 'vscrollbar_selected_xoffset', 'vscrollbar_selected_xpos', 'vscrollbar_selected_xsize', 'vscrollbar_selected_xysize', 'vscrollbar_selected_yalign', 'vscrollbar_selected_yanchor', 'vscrollbar_selected_ycenter',
                    'vscrollbar_selected_yfill', 'vscrollbar_selected_ymaximum', 'vscrollbar_selected_yoffset', 'vscrollbar_selected_ypos',
                    'vscrollbar_selected_ysize', 'vscrollbar_thumb', 'vscrollbar_thumb_offset', 'vscrollbar_thumb_shadow',
                    'vscrollbar_tooltip', 'vscrollbar_top_bar', 'vscrollbar_top_gutter', 'vscrollbar_unscrollable',
                    'vscrollbar_xalign', 'vscrollbar_xanchor', 'vscrollbar_xcenter', 'vscrollbar_xfill', 'vscrollbar_xmaximum',
                    'vscrollbar_xoffset', 'vscrollbar_xpos', 'vscrollbar_xsize', 'vscrollbar_xysize', 'vscrollbar_yalign',
                    'vscrollbar_yanchor', 'vscrollbar_ycenter', 'vscrollbar_yfill', 'vscrollbar_ymaximum', 'vscrollbar_yoffset',
                    'vscrollbar_ypos', 'vscrollbar_ysize', 'width', 'xadjustment', 'xalign', 'xanchor', 'xanchoraround',
                    'xaround', 'xcenter', 'xfill', 'xfit', 'xinitial', 'xmargin', 'xmaximum', 'xminimum', 'xoffset',
                    'xpadding', 'xpan', 'xpos', 'xsize', 'xspacing', 'xtile', 'xysize', 'xzoom', 'yadjustment', 'yalign', 'yanchor',
                    'yanchoraround', 'yaround', 'ycenter', 'yfill', 'yfit', 'yinitial', 'ymargin', 'ymaximum', 'yminimum', 'yoffset',
                    'ypadding', 'ypan', 'ypos', 'ysize', 'yspacing', 'ytile', 'yzoom', 'zoom'), prefix=r"( {4}){2,}", suffix=r"\b"), Renpy.Properties)
        ],
        "screen_actions": [
            (words(("Call", "Hide", "Jump", "NullAction", "Return", "Show",
                    "ShowTransient", "ToggleScreen", "AddToSet", "RemoveFromSet",
                    "SetDict", "SetField", "SetLocalVariable", "SetScreenVariable",
                    "SetVariable", "ToggleDict", "ToggleField", "ToggleLocalVariable",
                    "ToggleScreenVariable", "ToggleSetMembership", "ToggleVariable",
                    "MainMenu", "Quit", "ShowMenu", "Start", "FileAction",
                    "FileDelete", "FileLoad", "FilePage", "FilePageNext",
                    "FileSave", "FileTakeScreenshot", "QuickLoad",
                    "QuickSave", "PauseAudio", "Play", "Queue", "SetMixer",
                    "SetMute", "Stop", "ToggleMute", "Confirm", "DisableAllInputValues",
                    "Function", "Help", "HideInterface", "If", "InvertSelected",
                    "MouseMove", "Notify", "OpenURL", "QueueEvent", "RestartStatement",
                    "RollForward", "Rollback", "RollbackToIdentifier",
                    "Screenshot", "Scroll", "SelectedIf", "SensitiveIf", "Skip",
                    "With", "AnimatedValue", "AudioPositionValue", "DictValue",
                    "FieldValue", "MixerValue", "ScreenVariableValue", "StaticValue",
                    "VariableValue", "XScrollValue", "YScrollValue", "DictInputValue",
                    "FieldInputValue", "FilePageNameInputValue", "ScreenVariableInputValue",
                    "VariableInputValue", "Preference", "GamepadCalibrate", "GamepadExists",
                    "FileCurrentPage", "FileCurrentScreenshot", "FileJson", "FileLoadable",
                    "FileNewest", "FilePageName", "FileSaveName", "FileScreenshot", "FileSlotName",
                    "FileTime", "FileUsedSlot", "SideImage", "GetTooltip"), prefix=r' ', suffix=r"\b"), Renpy.Screen.Actions)
        ],
        'builtins': [
            (words((
                '__import__', 'abs', 'all', 'any', 'apply', 'basestring', 'bin',
                'bool', 'buffer', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod',
                'cmp', 'coerce', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
                'enumerate', 'eval', 'execfile', 'exit', 'file', 'filter', 'float',
                'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id',
                'input', 'int', 'intern', 'isinstance', 'issubclass', 'iter', 'len',
                'list', 'locals', 'long', 'map', 'max', 'min', 'next', 'object',
                'oct', 'open', 'ord', 'pow', 'property', 'range', 'raw_input', 'reduce',
                'reload', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
                'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
                'unichr', 'unicode', 'vars', 'xrange', 'zip'),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            (r'(?<!\.)(self|None|Ellipsis|NotImplemented|False|True|cls'
             r')\b', Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'DeprecationWarning', 'EOFError', 'EnvironmentError',
                'Exception', 'FloatingPointError', 'FutureWarning', 'GeneratorExit',
                'IOError', 'ImportError', 'ImportWarning', 'IndentationError',
                'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
                'MemoryError', 'ModuleNotFoundError', 'NameError', 'NotImplemented', 'NotImplementedError',
                'OSError', 'OverflowError', 'OverflowWarning', 'PendingDeprecationWarning',
                'RecursionError', 'ReferenceError', 'RuntimeError', 'RuntimeWarning', 'StandardError',
                'StopIteration', 'StopAsyncIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
                'SystemExit', 'TabError', 'TypeError', 'UnboundLocalError',
                'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError',
                'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning',
                'ValueError', 'VMSError', 'Warning', 'WindowsError',
                'ZeroDivisionError'), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Exception),
        ],
        'magicfuncs': [
            (words((
                '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
                '__complex__', '__contains__', '__del__', '__delattr__', '__delete__',
                '__delitem__', '__delslice__', '__div__', '__divmod__', '__enter__',
                '__eq__', '__exit__', '__float__', '__floordiv__', '__ge__', '__get__',
                '__getattr__', '__getattribute__', '__getitem__', '__getslice__', '__gt__',
                '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__', '__ifloordiv__',
                '__ilshift__', '__imod__', '__imul__', '__index__', '__init__',
                '__instancecheck__', '__int__', '__invert__', '__iop__', '__ior__',
                '__ipow__', '__irshift__', '__isub__', '__iter__', '__itruediv__',
                '__ixor__', '__le__', '__len__', '__long__', '__lshift__', '__lt__',
                '__missing__', '__mod__', '__mul__', '__ne__', '__neg__', '__new__',
                '__nonzero__', '__oct__', '__op__', '__or__', '__pos__', '__pow__',
                '__radd__', '__rand__', '__rcmp__', '__rdiv__', '__rdivmod__', '__repr__',
                '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__',
                '__rop__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
                '__rtruediv__', '__rxor__', '__set__', '__setattr__', '__setitem__',
                '__setslice__', '__str__', '__sub__', '__subclasscheck__', '__truediv__',
                '__unicode__', '__xor__'), suffix=r'\b'),
             Name.Function.Magic),
        ],
        'magicvars': [
            (words((
                '__bases__', '__class__', '__closure__', '__code__', '__defaults__',
                '__dict__', '__doc__', '__file__', '__func__', '__globals__',
                '__metaclass__', '__module__', '__mro__', '__name__', '__self__',
                '__slots__', '__weakref__'),
                suffix=r'\b'),
             Name.Variable.Magic),
        ],
        'numbers': [
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'0[0-7]+j?', Number.Oct),
            (r'0[bB][01]+', Number.Bin),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+j?', Number.Integer)
        ],
        'backtick': [
            ('`.*?`', String.Backtick),
        ],
        'name': [
            (r'@[\w.]+', Name.Decorator),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'funcname': [
            include('magicfuncs'),
            (r'[a-zA-Z_]\w*', Name.Function, '#pop'),
            default('#pop'),
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'(?:[ \t]|\\\n)+', Text),
            (r'as\b', Keyword.Namespace),
            (r',', Operator),
            (r'[a-zA-Z_][\w.]*', Name.Namespace),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(?:[ \t]|\\\n)+', Text),
            (r'import\b', Keyword.Namespace, '#pop'),
            # if None occurs here, it's "raise x from None", since None can
            # never be a module name
            (r'None\b', Name.Builtin.Pseudo, '#pop'),
            # sadly, in "raise x from y" y will be highlighted as namespace too
            (r'[a-zA-Z_.][\w.]*', Name.Namespace),
            # anything else here also means "raise x from y" and is therefore
            # not an error
            default('#pop'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single')
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double)
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single)
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'pythonw?(2(\.\d)?)?') or \
            'import ' in text[:1000]


class RenpyConsoleLexer(Lexer):
    """
    For Renpy console output or doctests, such as:

    .. sourcecode:: rpycon

        >>> a = 'foo'
        >>> print a
        foo
        >>> 1 / 0
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        ZeroDivisionError: integer division or modulo by zero

        .. versionadded:: 0.1
    """
    name = 'Renpy console session'
    aliases = ['rpycon']

    def __init__(self, **options):
        Lexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        pylexer = RenpyLexer(**self.options)
        tblexer = RenpyTracebackLexer(**self.options)

        curcode = ''
        insertions = []
        curtb = ''
        tbindex = 0
        tb = 0
        for match in line_re.finditer(text):
            line = match.group()
            if line.startswith(u'>>> ') or line.startswith(u'... '):
                tb = 0
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, line[:4])]))
                curcode += line[4:]
            elif line.rstrip() == u'...' and not tb:
                # only a new >>> prompt can end an exception block
                # otherwise an ellipsis in place of the traceback frames
                # will be mishandled
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, u'...')]))
                curcode += line[3:]
            else:
                if curcode:
                    for item in do_insertions(
                            insertions,
                            pylexer.get_tokens_unprocessed(curcode)):
                        yield item
                    curcode = ''
                    insertions = []
                if (line.startswith(u'Traceback (most recent call last):') or
                        re.match(u'  File "[^"]+", line \\d+\\n$', line)):
                    tb = 1
                    curtb = line
                    tbindex = match.start()
                elif line == 'KeyboardInterrupt\n':
                    yield match.start(), Name.Class, line
                elif tb:
                    curtb += line
                    if not (line.startswith(' ') or line.strip() == u'...'):
                        tb = 0
                        for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                            yield tbindex + i, t, v
                        curtb = ''
                else:
                    yield match.start(), Generic.Output, line
        if curcode:
            for item in do_insertions(insertions,
                                      pylexer.get_tokens_unprocessed(curcode)):
                yield item
        if curtb:
            for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                yield tbindex + i, t, v


class RenpyTracebackLexer(RegexLexer):
    """
    For Renpy tracebacks.

    .. versionadded:: 0.1
    """

    name = 'Renpy Traceback'
    aliases = ['rpytb']
    filenames = ['*.rpytb']

    tokens = {
        'root': [
            # Cover both (most recent call last) and (innermost last)
            # The optional ^C allows us to catch keyboard interrupt signals.
            (r'^(\^C)?(Traceback.*\n)',
             bygroups(Text, Generic.Traceback), 'intb'),
            # SyntaxError starts with this.
            (r'^(?=  File "[^"]+", line \d+)', Generic.Traceback, 'intb'),
            (r'^.*\n', Other),
        ],
        'intb': [
            (r'^(  File )("[^"]+")(, line )(\d+)(, in )(.+)(\n)',
             bygroups(Text, Name.Builtin, Text, Number, Text, Name, Text)),
            (r'^(  File )("[^"]+")(, line )(\d+)(\n)',
             bygroups(Text, Name.Builtin, Text, Number, Text)),
            (r'^(    )(.+)(\n)',
             bygroups(Text, using(RenpyLexer), Text)),
            (r'^([ \t]*)(\.\.\.)(\n)',
             bygroups(Text, Comment, Text)),  # for doctests...
            (r'^([^:]+)(: )(.+)(\n)',
             bygroups(Generic.Error, Text, Name, Text), '#pop'),
            (r'^([a-zA-Z_]\w*)(:?\n)',
             bygroups(Generic.Error, Text), '#pop')
        ],
    }


class NullLexer(RegexLexer):
    name = 'Null'
    aliases = ['null']
    filenames = ['*.null']

    tokens = {
        'root': [
            (r' .*\n', Text),
        ]
    }
