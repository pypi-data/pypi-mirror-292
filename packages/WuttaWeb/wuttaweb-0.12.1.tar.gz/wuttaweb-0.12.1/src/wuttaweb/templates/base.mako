## -*- coding: utf-8; -*-
<%namespace name="base_meta" file="/base_meta.mako" />
<%namespace file="/wutta-components.mako" import="make_wutta_components" />
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>${base_meta.global_title()} &raquo; ${capture(self.title)|n}</title>
    ${base_meta.favicon()}
    ${self.header_core()}
    ${self.head_tags()}
  </head>
  <body>
    <div id="app" style="height: 100%;">
      <whole-page />
    </div>

    ## nb. sometimes a template needs to define something
    ## before the body content proper is rendered
    ${self.before_content()}

    ## content body from derived/child template
    ${self.body()}

    ## Vue app
    ${self.render_vue_templates()}
    ${self.modify_vue_vars()}
    ${self.make_vue_components()}
    ${self.make_vue_app()}
  </body>
</html>

## nb. this becomes part of the page <title> tag within <head>
## it also is used as default value for content_title() below
<%def name="title()"></%def>

## nb. this is the "content title" as shown on screen, within the
## "hero bar" just below the "index title"
<%def name="content_title()">${self.title()}</%def>

<%def name="header_core()">
  ${self.core_javascript()}
  ${self.extra_javascript()}
  ${self.core_styles()}
  ${self.extra_styles()}
</%def>

<%def name="core_javascript()">
  ${self.vuejs()}
  ${self.buefy()}
  ${self.fontawesome()}
  ${self.hamburger_menu_js()}
</%def>

<%def name="hamburger_menu_js()">
  <script>

    ## NOTE: this code was copied from
    ## https://bulma.io/documentation/components/navbar/#navbar-menu

    document.addEventListener('DOMContentLoaded', () => {

        // Get all "navbar-burger" elements
        const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0)

        // Add a click event on each of them
        $navbarBurgers.forEach( el => {
            el.addEventListener('click', () => {

                // Get the target from the "data-target" attribute
                const target = el.dataset.target
                const $target = document.getElementById(target)

                // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
                el.classList.toggle('is-active')
                $target.classList.toggle('is-active')

            })
        })
    })

  </script>
</%def>

<%def name="vuejs()">
  ${h.javascript_link(h.get_liburl(request, 'vue'))}
  ${h.javascript_link(h.get_liburl(request, 'vue_resource'))}
</%def>

<%def name="buefy()">
  ${h.javascript_link(h.get_liburl(request, 'buefy'))}
</%def>

<%def name="fontawesome()">
  <script defer src="${h.get_liburl(request, 'fontawesome')}"></script>
</%def>

<%def name="extra_javascript()"></%def>

<%def name="core_styles()">
  ${self.buefy_styles()}
  ${self.base_styles()}
</%def>

<%def name="buefy_styles()">
  ${h.stylesheet_link(h.get_liburl(request, 'buefy.css'))}
</%def>

<%def name="base_styles()">
  <style>

    ##############################
    ## page
    ##############################

    ## nb. helps force footer to bottom of screen
    html, body {
        height: 100%;
    }

    % if not request.wutta_config.production():
        html, .navbar, .footer {
          background-image: url(${request.static_url('wuttaweb:static/img/testing.png')});
        }
    % endif

    ## nb. this refers to the "home link" app title, next to small
    ## header logo in top left of screen
    #navbar-brand-title {
        font-weight: bold;
        margin-left: 0.3rem;
    }

    #header-index-title {
        display: flex;
        gap: 1.5rem;
        padding-left: 0.5rem;
    }

    h1.title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0 !important;
    }

    #content-title h1 {
        max-width: 50%;
        overflow: hidden;
        padding-left: 0.5rem;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .wutta-page-content-wrapper {
        height: 100%;
    }

    ##############################
    ## grids
    ##############################

    .wutta-filter {
        display: flex;
        gap: 0.5rem;
    }

    .wutta-filter .button.filter-toggle {
        justify-content: left;
    }

    .wutta-filter .button.filter-toggle,
    .wutta-filter .filter-verb {
        min-width: 15rem;
    }

    .wutta-filter .filter-verb .select,
    .wutta-filter .filter-verb .select select {
        width: 100%;
    }

    ##############################
    ## forms
    ##############################

    .wutta-form-wrapper {
        margin-left: 5rem;
        margin-top: 2rem;
        width: 50%;
    }

  </style>
</%def>

<%def name="extra_styles()">
  ${base_meta.extra_styles()}
</%def>

<%def name="head_tags()"></%def>

<%def name="render_vue_template_whole_page()">
  <script type="text/x-template" id="whole-page-template">

    ## nb. the whole-page contains 3 elements:
    ## 1) header-wrapper
    ## 2) content-wrapper
    ## 3) footer
    <div id="whole-page"
         style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">

      ## nb. the header-wrapper contains 2 elements:
      ## 1) header proper (menu + index title area)
      ## 2) page/content title area
      <div class="header-wrapper">

        ## nb. the header proper contains 2 elements:
        ## 1) menu bar
        ## 2) index title area
        <header>

          ## nb. this is the main menu bar
          <nav class="navbar" role="navigation" aria-label="main navigation">
            ${self.render_navbar_brand()}
            ${self.render_navbar_menu()}
          </nav>

          ## nb. this is the "index title" area
          <nav class="level" style="margin: 0.5rem 0.5rem 0.5rem auto;">

            ## nb. this is the index title proper
            <div class="level-left">
              <div id="header-index-title" class="level-item">
                % if index_title:
                    % if index_url:
                        <h1 class="title">${h.link_to(index_title, index_url)}</h1>
                    % else:
                        <h1 class="title">${index_title}</h1>
                    % endif
                    % if master and master.creatable and not master.creating and master.has_perm('create'):
                        <wutta-button once type="is-primary"
                                      tag="a" href="${url(f'{route_prefix}.create')}"
                                      icon-left="plus"
                                      label="Create New" />
                    % endif
                % endif
              </div>
            </div>

            ## nb. this is a utility area for the master context
            <div class="level-right">

              ## Configure button
              % if master and master.configurable and not master.configuring and master.has_perm('configure'):
                  <div class="level-item">
                    <wutta-button once type="is-primary"
                                  tag="a" href="${url(f'{route_prefix}.configure')}"
                                  icon-left="cog"
                                  label="Configure" />
                  </div>
              % endif

              ${self.render_theme_picker()}
              ${self.render_feedback_button()}

            </div>
          </nav>
        </header>

        ## nb. the page / content title area (aka. hero bar)
        % if capture(self.content_title):
            <section id="content-title"
                     class="has-background-primary">
              <div style="display: flex; align-items: center; padding: 0.5rem;">

                <h1 class="title has-text-white"
                    v-html="contentTitleHTML">
                </h1>

                <div style="flex-grow: 1; display: flex; gap: 0.5rem;">
                  ${self.render_instance_header_title_extras()}
                </div>

                <div style="display: flex; gap: 0.5rem;">
                  ${self.render_instance_header_buttons()}
                </div>

              </div>
            </section>
        % endif

      </div> <!-- header-wrapper -->

      ## nb. the page content area
      <div class="content-wrapper"
           style="flex-grow: 1; padding: 0.5rem;">
        <section id="page-body" style="height: 100%;">

          % if request.session.peek_flash('error'):
              % for error in request.session.pop_flash('error'):
                  <b-notification type="is-warning">
                    ${error}
                  </b-notification>
              % endfor
          % endif

          % if request.session.peek_flash('warning'):
              % for msg in request.session.pop_flash('warning'):
                  <b-notification type="is-warning">
                    ${msg}
                  </b-notification>
              % endfor
          % endif

          % if request.session.peek_flash():
              % for msg in request.session.pop_flash():
                  <b-notification type="is-info">
                    ${msg}
                  </b-notification>
              % endfor
          % endif

          <div style="height: 100%;">
            ${self.render_this_page_component()}
          </div>
        </section>
      </div><!-- content-wrapper -->

      ## nb. the page footer
      <footer class="footer">
        <div class="content">
          ${base_meta.footer()}
        </div>
      </footer>

    </div>
  </script>
</%def>

<%def name="render_navbar_brand()">
  <div class="navbar-brand">
    <a class="navbar-item" href="${url('home')}">
      <div style="display: flex; align-items: center;">
        ${base_meta.header_logo()}
        <div id="navbar-brand-title">
          ${base_meta.global_title()}
        </div>
      </div>
    </a>
    <a role="button" class="navbar-burger" data-target="navbar-menu" aria-label="menu" aria-expanded="false">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>
</%def>

<%def name="render_navbar_menu()">
  <div class="navbar-menu" id="navbar-menu">
    ${self.render_navbar_start()}
    ${self.render_navbar_end()}
  </div>
</%def>

<%def name="render_navbar_start()">
  <div class="navbar-start">

    % for topitem in menus:
        % if topitem['is_link']:
            ${h.link_to(topitem['title'], topitem['url'], target=topitem['target'], class_='navbar-item')}
        % else:
            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">${topitem['title']}</a>
              <div class="navbar-dropdown">
                % for item in topitem['items']:
                    % if item['is_menu']:
                        <% item_hash = id(item) %>
                        <% toggle = 'menu_{}_shown'.format(item_hash) %>
                        <div>
                          <a class="navbar-link" @click.prevent="toggleNestedMenu('${item_hash}')">
                            ${item['title']}
                          </a>
                        </div>
                        % for subitem in item['items']:
                            % if subitem['is_sep']:
                                <hr class="navbar-divider" v-show="${toggle}">
                            % else:
                                ${h.link_to("{}".format(subitem['title']), subitem['url'], class_='navbar-item nested', target=subitem['target'], **{'v-show': toggle})}
                            % endif
                        % endfor
                    % else:
                        % if item['is_sep']:
                            <hr class="navbar-divider">
                        % else:
                            ${h.link_to(item['title'], item['url'], class_='navbar-item', target=item['target'])}
                        % endif
                    % endif
                % endfor
              </div>
            </div>
        % endif
    % endfor

  </div>
</%def>

<%def name="render_navbar_end()">
  <div class="navbar-end">
    ${self.render_user_menu()}
  </div>
</%def>

<%def name="render_theme_picker()"></%def>

<%def name="render_feedback_button()"></%def>

<%def name="render_vue_script_whole_page()">
  <script>

    const WholePage = {
        template: '#whole-page-template',
        computed: {},

        mounted() {
            for (let hook of this.mountedHooks) {
                hook(this)
            }
        },

        methods: {

            changeContentTitle(newTitle) {
                this.contentTitleHTML = newTitle
            },

            toggleNestedMenu(hash) {
                const key = 'menu_' + hash + '_shown'
                this[key] = !this[key]
            },

            % if request.is_admin:

                startBeingRoot() {
                    this.$refs.startBeingRootForm.submit()
                },

                stopBeingRoot() {
                    this.$refs.stopBeingRootForm.submit()
                },

            % endif
        },
    }

    const WholePageData = {
        contentTitleHTML: ${json.dumps(capture(self.content_title))|n},
        referrer: location.href,
        mountedHooks: [],
    }

    ## declare nested menu visibility toggle flags
    % for topitem in menus:
        % if topitem['is_menu']:
            % for item in topitem['items']:
                % if item['is_menu']:
                    WholePageData.menu_${id(item)}_shown = false
                % endif
            % endfor
        % endif
    % endfor

  </script>
</%def>

<%def name="before_content()"></%def>

<%def name="render_this_page_component()">
  <this-page @change-content-title="changeContentTitle" />
</%def>

<%def name="render_user_menu()">
  % if request.user:
      <div class="navbar-item has-dropdown is-hoverable">
        <a class="navbar-link ${'has-background-danger has-text-white' if request.is_root else ''}">${request.user}</a>
        <div class="navbar-dropdown">
          % if request.is_root:
              ${h.form(url('stop_root'), ref='stopBeingRootForm')}
              ${h.csrf_token(request)}
              <input type="hidden" name="referrer" value="${request.current_route_url()}" />
              <a @click="stopBeingRoot()"
                 class="navbar-item has-background-danger has-text-white">
                Stop being root
              </a>
              ${h.end_form()}
          % elif request.is_admin:
              ${h.form(url('become_root'), ref='startBeingRootForm')}
              ${h.csrf_token(request)}
              <input type="hidden" name="referrer" value="${request.url}" />
              <a @click="startBeingRoot()"
                 class="navbar-item has-background-danger has-text-white">
                Become root
              </a>
              ${h.end_form()}
          % endif
          ${h.link_to("Change Password", url('change_password'), class_='navbar-item')}
          ${h.link_to("Logout", url('logout'), class_='navbar-item')}
        </div>
      </div>
  % else:
      ${h.link_to("Login", url('login'), class_='navbar-item')}
  % endif
</%def>

<%def name="render_instance_header_title_extras()"></%def>

<%def name="render_instance_header_buttons()">
  ${self.render_crud_header_buttons()}
  ${self.render_prevnext_header_buttons()}
</%def>

<%def name="render_crud_header_buttons()">
  % if master:
      % if master.viewing:
          % if instance_editable and master.has_perm('edit'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('edit', instance)}"
                            icon-left="edit"
                            label="Edit This" />
          % endif
          % if instance_deletable and master.has_perm('delete'):
              <wutta-button once type="is-danger"
                            tag="a" href="${master.get_action_url('delete', instance)}"
                            icon-left="trash"
                            label="Delete This" />
          % endif
      % elif master.editing:
          % if master.has_perm('view'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('view', instance)}"
                            icon-left="eye"
                            label="View This" />
          % endif
          % if instance_deletable and master.has_perm('delete'):
              <wutta-button once type="is-danger"
                            tag="a" href="${master.get_action_url('delete', instance)}"
                            icon-left="trash"
                            label="Delete This" />
          % endif
      % elif master.deleting:
          % if master.has_perm('view'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('view', instance)}"
                            icon-left="eye"
                            label="View This" />
          % endif
          % if instance_editable and master.has_perm('edit'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('edit', instance)}"
                            icon-left="edit"
                            label="Edit This" />
          % endif
      % endif
  % endif
</%def>

<%def name="render_prevnext_header_buttons()"></%def>

##############################
## vue components + app
##############################

<%def name="render_vue_templates()">
  ${self.render_vue_template_whole_page()}
  ${self.render_vue_script_whole_page()}
</%def>

<%def name="modify_vue_vars()"></%def>

<%def name="make_vue_components()">
  ${make_wutta_components()}
  <script>
    WholePage.data = function() { return WholePageData }
    Vue.component('whole-page', WholePage)
  </script>
</%def>

<%def name="make_vue_app()">
  <script>
    new Vue({
        el: '#app'
    })
  </script>
</%def>
