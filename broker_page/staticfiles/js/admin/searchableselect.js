/*
|-----------------------------------------------------------------------------
| Searchable <select/> element
|-----------------------------------------------------------------------------
|
| Example use (vanilla js): --------------------------------------------------
|
|   <select id="select">
|     <option value="42">Forty two</option>
|   </select>
| 
|   var elem = document.getElementById('select');
|   var select = new Select({ elem: elem });
|   select.render();
|
| Example use (jQuery opt-in): -----------------------------------------------
|
|   <select id="select">
|     <option value="42">Forty two</option>
|   </select>
|   
|   $('#select').searchableSelect();
|
| Example use (data-* API): --------------------------------------------------
|   
|   <select data-searchable="select">
|     <option value="42">Forty two</option>
|   </select>
|
|-----------------------------------------------------------------------------
*/

(function($){
    
    'use strict';
  
    /*
    |-------------------------------------------------------------------------
    | Debug: write line
    |-------------------------------------------------------------------------
    */

    function writeLn (msg) {
        var elem = document.getElementById('debug');
        var html = elem.innerHTML;
        elem.innerHTML = html + msg + '\n';
    }
  
    /*
    |-------------------------------------------------------------------------
    | Option model
    |-------------------------------------------------------------------------
    */
    
    /**
     * Option constructor
     * @param   object attrs Attributes hash
     * @returns void
     */
    
    var Option = function (attrs) {
        this.label = function () {
            return attrs.label;
        }
        this.value = function () {
            return attrs.hasOwnProperty('value') ? attrs.value : attrs.label;
        }
        if (attrs.hasOwnProperty('selected')) {
            this.selected = attrs.selected;
        }
        if (attrs.hasOwnProperty('filtered')) {
            this.filtered = attrs.filtered;
        }
        return this;
    }

    Option.prototype = {

        constructor: Option, // Constructor
        
        selected: false, // Denotes whether or not selected
        
        filtered: false, // Denotes whether or not filtered
        
        /**
         * Sets the selected property to true
         * @returns this
         */
        
        select: function () {
            this.selected = true;
            return this;
        },
        
        /**
         * Sets the selected property to false
         * @returns this
         */
        
        deselect: function () {
            this.selected = false;
        },
        
        /**
         * Sets the filtered property to true -this option will be omitted
         * from rendered options list
         * @returns this
         */
        
        filter: function () {
            this.filtered = true;
        },
        
        /**
         * Sets the filtered property to false -this option will not be
         * omitted from rendered options list
         * @returns this
         */
        
        unfilter: function () {
            this.filtered = false;
        },

    }
  
    /*
    |-------------------------------------------------------------------------
    | Option collection
    |-------------------------------------------------------------------------
    */
    
    /**
     * The Options constructor
     * @param {Array} Array of Option instance -or array of attr hashes
     */
    
    var Options = function (items) {
        items || (items = []);
        var len = items.length, i = 0;
        for (; i < len; i++) this.push(items[i]);
    }

    Options.prototype = {

        constructor: Options, // Constructor
        
        items: [], // Array of options
        
        /**
         * Iterates over items, yielding each in turn to an iteratee
         * function
         * @param   {function} iteratee Called on each iteration
         * @returns this
         */
        
        each: function (iteratee) {
            var items = this.items;
            var len = items.length, i = 0;
            for (; i < len; i++) iteratee(items[i], i, items);
            return this;
        },
        
        /**
         * Pushes an Option to the item stack
         * @param   {object|Option} item An Option instance or hash of attrs
         * @returns this
         */
        
        push: function (item) {
            if (!(item instanceof Option)) item = new Option(item);
            this.items.push(item);
            return this;
        },
        
        /**
         * Gets an item matching the provided value (if any)
         * @param   {[[Type]]} value The value to search for
         * @returns {Option} The Option instance with the given value
         */
        
        get: function (value) {
            var retval = null;
            this.each(function(model){
                if (retval) return;
                if (model.value() == value) retval = model;
            });
            return retval;
        },
        
        /**
         * Returns the selected item -undefined otherwise
         * @returns {Option} the selected Option instance
         */
        
        selected: function () {
            var retval = null;
            this.each(function(model){
                if (retval) return;
                if (model.selected == true) retval = model;
            });
            return retval;
        }

    }
  
    /*
    |-------------------------------------------------------------------------
    | Select control element
    |-------------------------------------------------------------------------
    */
    
    /**
     * Control constructor
     * @param {object} options
     */
    
    var SelectControl = function (options) {
        if (options.hasOwnProperty('value')) {
            this.value = options.value;
        }
        this.initialize(options);
    }

    SelectControl.prototype = {

        constructor: SelectControl, // Constructor
        
        elem: null, // DOM Element Object of the parent <div>
        
        label: null, // DOM Element Object of the <span> label
        
        caret: null, // DOM Element Object of the <span> caret
        
        value: 'Select one', // Value to be displayed

        focused: false, // Denotes whether or not focused
        
        /**
         * Intialize
         * @param {object} options
         * @returns this
         */
        
        initialize: function (options) {
            var elem = document.createElement('div');
            elem.classList.add('select-control');
            elem.classList.add('form-control');
            this.elem = elem;
            return this;
        },
        
        /**
         * Renders the element
         * @returns this
         */
        
        render: function () {
            var elem = this.elem;
            var label = document.createElement('span');
            var caret = document.createElement('span');
            elem.innerHTML = '';
            label.classList.add('select-control-label');
            label.innerHTML = this.value;
            caret.classList.add('fa');
            caret.classList.add('fa-caret-down');
            caret.classList.add('select-control-caret');
            elem.appendChild(label);
            elem.appendChild(caret);
            this.caret = caret;
            this.label = label;
            return this;
        },
        
        /**
         * Sets the display value
         * @param {string} value The display value
         * @returns this
         */
        
        setLabel: function (value) {
            this.value = value;
            this.label.innerHTML = value;
            return this;
        },
        
        /**
         * Sets the element's focus state
         * @returns this
         */
        
        focus: function () {
            this.focused = true;
            this.elem.classList.add('focus');
            return this;
        },
        
        /**
         * Unsets the element's focus state
         * @returns this
         */
        
        blur: function () {
            this.focused = false;
            this.elem.classList.remove('focus');
            return this;
        },
        
    }
  
    /*
    |-------------------------------------------------------------------------
    | Select list element
    |-------------------------------------------------------------------------
    */
    
    /**
     * List constructor
     * @param {object} options
     */
    
    var SelectList = function (options) {
        this.collection = options.collection;
        this.initialize(options);
    }
    
    SelectList.prototype = {

        constructor: SelectList, // Constructor
        
        collection: null, // Instance of Options
        
        elem: null, // DOM Element Object of the parent <div>
        
        input: null, // DOM Element Object of the <input> searchbox
        
        opened: false, // Denotes whether or not opened
        
        /**
         * Intialize
         * @param {object} options
         * @returns this
         */
        
        initialize: function (options) {
            var elem = document.createElement('div');
            elem.classList.add('select-list');
            elem.classList.add('d-none');
            this.elem = elem;
            return this;
        },
        
        /**
         * Renders the element
         * @returns this
         */
        
        render: function () {
            var elem = this.elem, item;
            var group = document.createElement('div');
            var input = document.createElement('input');
            group.classList.add('input-group');
            input.type = 'search';
            input.classList.add('select-list-searchbox');
            input.classList.add('form-control');
            elem.appendChild(input);
            this.collection.each(function(model){
                item = new SelectListItem({model: model});
                item.render();
                elem.appendChild(item.elem);
            });
            return this;
        },
        
        /**
         * Unhides the element
         * @returns this
         */
        
        show: function () {
            this.opened = true;
            this.elem.classList.remove('d-none');
            return this;
        },
        
        /**
         * Hides the element
         * @returns this
         */
        
        hide: function () {
            this.opened = false;
            this.elem.classList.add('d-none');
        },
        
        /**
         * Toggles the element's visibility
         * @returns this
         */
        
        toggle: function () {
            return this.opened ? this.hide() : this.show();
        }
        
    }
  
    /*
    |-------------------------------------------------------------------------
    | Select list item element
    |-------------------------------------------------------------------------
    */
    
    /**
     * List item constructor
     * @param {object} options
     */
    
    var SelectListItem = function (options) {
        this.model = options.model;
        this.initialize(options);
    }
    
    SelectListItem.prototype = {
        
        constructor: SelectListItem, // Constructor
        
        model: null, // Instance of Option
        
        elem: null, // DOM Element Object of the parent <div>
        
        /**
         * Intialize
         * @param {object} options
         * @returns this
         */
        
        initialize: function () {
            var elem = document.createElement('div');
            elem.setAttribute('data-value', this.model.value());
            elem.classList.add('select-list-item');
            this.elem = elem;
            return this;
        },
        
        /**
         * Renders the element
         * @returns this
         */
        
        render: function () {
            this.elem.innerHTML = this.model.label();
            return this;
        }

    }
  
    /*
    |-------------------------------------------------------------------------
    | Select element
    |-------------------------------------------------------------------------
    */
    
    /**
     * Select constructor
     * @param {object} options
     */
    
    var Select = function (options) {
        this.elem = options.elem;
        this.initialize(options);
    }

    Select.prototype = {

        constructor: Select, // Constructor
        
        collection: null, // Instance of Options
        
        elem: null, // DOM Element Object of original <select>
        
        $elem: null, // jQuery handle of original <select>
        
        wrapper: null, // DOM Element Object of the parent <div>
        
        $wrapper: null, // jQuery handle of parent <div>
        
        control: null, // Instance of SelectControl
        
        $control: null, // jQuery handle of control's element
        
        list: null, // Instance of SelectList
        
        $list: null, // jQuery handle of list's element
        
        /**
         * Intialize
         * @param {object} options
         * @returns this
         */
        
        initialize: function (options) {
            this.initializeCollection(options)
                .initializeElement(options)
                .initializeControl(options)
                .initializeList(options);
            return this;
        },
        
        /**
         * Intializes the collection
         * @param {object} options
         * @returns this
         */
        
        initializeCollection: function (options) {
            var select = this.elem;
            var children = select.options;
            var child;
            var html;
            var items = [];
            var len = children.length;
            var i = 0;
            for (; i < len; i++) {
                child = children[i];
                html = child.innerHTML;
                items.push({
                    label: html
                    , value: child.value ? child.value : html
                    , selected: i == 0
                });
            }
            this.collection = new Options(items);
            return this;
        },
        
        /**
         * Intializes the element
         * @param {object} options
         * @returns this
         */
        
        initializeElement: function (options) {
            var self = this;
            var elem = this.elem;
            var wrapper = document.createElement('div');
            var $elem, $wrapper;
            wrapper.classList.add('select');
            elem.classList.add('d-none');
            elem.parentNode.insertBefore(wrapper, elem.nextSibling);
            wrapper.appendChild(elem);
            $elem = $(elem);
            $wrapper = $(wrapper);
            $(document).on('click', function (e) { // Mock blur event
                if (!$wrapper.is(e.target) && $wrapper.has(e.target).length === 0) {
                    self.blur();
                    self.close();
                }
            });
            this.wrapper = wrapper;
            this.$elem = $elem;
            this.$wrapper = $wrapper;
            return this;
        },
        
        /**
         * Intializes the control element
         * @param {object} options
         * @returns this
         */
        
        initializeControl: function (options) {
            var self = this, elem = this.wrapper;
            var control = new SelectControl({}), $control;
            elem.appendChild(control.elem);
            $control = $(control.elem);
            $control.on('click', function () {
                if (!self.focused()) self.focus();
            });
            this.control = control;
            this.$control = $control;
            return this;
        },
        
        /**
         * Intializes the list element
         * @param {object} options
         * @returns this
         */
        
        initializeList: function () {
            var self = this, elem = this.wrapper;
            var list = new SelectList({
                collection: this.collection
            });
            var $control = this.$control, $list;
            elem.appendChild(list.elem);
            $list = $(list.elem);
            $control.on('click', function () {
                list.toggle();
            });
            $list.on('click', '.select-list-item', function (e) {
                var value = e.currentTarget.getAttribute('data-value');
                self.select(value);
            });
            this.list = list;
            this.$list = $list;
            return this;
        },
        
        /**
         * Renders the element
         * @returns this
         */
        
        render: function () {
            this.control.render();
            this.list.render();
            return this;
        },
        
        /**
         * Sets the control element's focus state
         * @returns this
         */
        
        focus: function () {
            this.control.focus();
            return this;
        },
        
        /**
         * Unsets the control element's focus state
         * @returns this
         */
        
        blur: function () {
            this.control.blur();
            return this;
        },
        
        /**
         * Denotes whether or not control element is focused
         * @returns {[[Type]]} [[Description]]
         */
        focused: function () {
            return this.control.focused;
        },
        
        /**
         * Shows the list element
         * @returns this
         */
        
        open: function () {
            this.list.show();
            return this;
        },
        
        /**
         * Hides the list element
         * @returns this
         */
        
        close: function () {
            this.list.hide();
            return this;
        },
        
        /**
         * Toggles the list element's state
         * @returns this
         */
        
        toggle: function () {
            this.list.toggle();
            return this;
        },
        
        /**
         * Selects an option of a given value
         * @param   {string} value Value
         * @returns {Option} The selected Option
         */
        
        select: function (value) {
            var collection = this.collection;
            var prev = collection.selected();
            if (prev) prev.deselect();
            var selected = this.collection.get(value);
            selected.select();
            this.control.setLabel(selected.label());
            this.value(selected.value());
            this.close();
            return selected;
        },
        
        /**
         * Value getter / setter
         * @param   {string} value Value
         * @returns this
         */
        
        value: function (value) {
            if (arguments.length == 0) return this.elem.value;
            this.elem.value = value;
            return this;
        },
        
    }

  /*
  |---------------------------------------------------------------------------
  | jQuery plugin
  |---------------------------------------------------------------------------
  */
  
  /*
  |---------------------------------------------------------------------------
  | Export Select constructor
  |---------------------------------------------------------------------------
  */

  this.Select = Select;
  
}.call(this, jQuery));



/*
|-----------------------------------------------------------------------------
| Example install
|-----------------------------------------------------------------------------
*/

$(function(){
  
  
  
  var select = new Select({
    elem: document.getElementById('select')
  });
  
  select.render();
  
  
  
});
