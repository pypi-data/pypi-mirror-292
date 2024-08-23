
<%def name="make_wutta_components()">
  ${self.make_wutta_button_component()}
  ${self.make_wutta_filter_component()}
  ${self.make_wutta_filter_value_component()}
</%def>

<%def name="make_wutta_button_component()">
  <script type="text/x-template" id="wutta-button-template">
    <b-button :type="type"
              :native-type="nativeType"
              :tag="tag"
              :href="href"
              :title="title"
              :disabled="buttonDisabled"
              @click="clicked"
              icon-pack="fas"
              :icon-left="iconLeft">
      {{ buttonLabel }}
    </b-button>
  </script>
  <script>
    const WuttaButton = {
        template: '#wutta-button-template',
        props: {
            type: String,
            nativeType: String,
            tag: String,
            href: String,
            label: String,
            title: String,
            iconLeft: String,
            working: String,
            workingLabel: String,
            disabled: Boolean,
            once: Boolean,
        },
        data() {
            return {
                currentLabel: null,
                currentDisabled: null,
            }
        },
        computed: {
            buttonLabel: function() {
                return this.currentLabel || this.label
            },
            buttonDisabled: function() {
                if (this.currentDisabled !== null) {
                    return this.currentDisabled
                }
                return this.disabled
            },
        },
        methods: {

            clicked(event) {
                if (this.once) {
                    this.currentDisabled = true
                    if (this.workingLabel) {
                        this.currentLabel = this.workingLabel
                    } else if (this.working) {
                        this.currentLabel = this.working + ", please wait..."
                    } else {
                        this.currentLabel = "Working, please wait..."
                    }
                }
            }
        },
    }
    Vue.component('wutta-button', WuttaButton)
  </script>
</%def>

<%def name="make_wutta_filter_component()">
  <script type="text/x-template" id="wutta-filter-template">
    <div v-show="filter.visible"
         class="wutta-filter">

      <b-button @click="filter.active = !filter.active"
                class="filter-toggle"
                icon-pack="fas"
                :icon-left="filter.active ? 'check' : null"
                :size="isSmall ? 'is-small' : null">
        {{ filter.label }}
      </b-button>

      <div v-show="filter.active"
           style="display: flex; gap: 0.5rem;">

        <b-select v-model="filter.verb"
                  class="filter-verb"
                  :size="isSmall ? 'is-small' : null">
          <option v-for="verb in filter.verbs"
                  :key="verb"
                  :value="verb">
            {{ verb }}
          </option>
        </b-select>

        <wutta-filter-value v-model="filter.value"
                            ref="filterValue"
                            :is-small="isSmall" />

      </div>
    </div>
  </script>
  <script>

    const WuttaFilter = {
        template: '#wutta-filter-template',
        props: {
            filter: Object,
            isSmall: Boolean,
        },

        methods: {

            focusValue: function() {
                this.$refs.filterValue.focus()
            }
        }
    }

    Vue.component('wutta-filter', WuttaFilter)

  </script>
</%def>

<%def name="make_wutta_filter_value_component()">
  <script type="text/x-template" id="wutta-filter-value-template">
    <div class="wutta-filter-value">

      <b-input v-model="inputValue"
               ref="valueInput"
               @input="val => $emit('input', val)"
               :size="isSmall ? 'is-small' : null" />

    </div>
  </script>
  <script>

    const WuttaFilterValue = {
        template: '#wutta-filter-value-template',
        props: {
            value: String,
            isSmall: Boolean,
        },

        data() {
            return {
                inputValue: this.value,
            }
        },

        methods: {

            focus: function() {
                this.$refs.valueInput.focus()
            }
        },
    }

    Vue.component('wutta-filter-value', WuttaFilterValue)

  </script>
</%def>
