## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />

<%def name="title()">Home</%def>

<%def name="page_content()">
  <div style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem;">
    <div>${base_meta.full_logo(image_url or None)}</div>
    <h1 class="is-size-1">Welcome to ${app.get_title()}</h1>
  </div>
</%def>
