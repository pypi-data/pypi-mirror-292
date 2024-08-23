## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">${index_title}</%def>

## nb. avoid hero bar for index page
<%def name="content_title()"></%def>

<%def name="page_content()">
  % if grid is not Undefined:
      ${grid.render_vue_tag()}
  % endif
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${self.render_vue_template_grid()}
</%def>

<%def name="render_vue_template_grid()">
  % if grid is not Undefined:
      ${grid.render_vue_template()}
  % endif
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if grid is not Undefined:
      ${grid.render_vue_finalize()}
  % endif
</%def>
