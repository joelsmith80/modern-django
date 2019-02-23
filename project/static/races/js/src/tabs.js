var raceTabs = (function($){

  $ = jQuery.noConflict();

  'use strict';  

  // placeholder for cached DOM elements
  var DOM = {};

  /* ===== private stuff ===== */

  function cacheDom(){
    DOM.$container = $("*[data-ui='tabs']");
    DOM.$nav = DOM.$container.find('nav');
    DOM.$navItems = DOM.$nav.find('li');
    DOM.$panels = DOM.$container.find('.panel');
  }

  function bindEvents(){
    // DOM.$switchToLoginLink.click(toggleToLogin);
    // DOM.$switchToRegisterLink.click(toggleToRegister);
    DOM.$navItems.find('a').click(fireSwitch);
  }

  function setInitialState(){
    var initialPanel = DOM.$panels.eq(0).attr('id');
    var initialTab = DOM.$navItems.eq(0).attr('id');
    hide_all_panels_but_this_one(initialPanel);
    mute_all_tabs_but_this_one(initialTab);
  }

  function hide_all_panels_but_this_one( id ){
    $(id).show();
    DOM.$panels.not(id).hide();
  }

  function mute_all_tabs_but_this_one( id ){
    $('#' + id).removeClass('muted');
    DOM.$navItems.not('#' + id ).addClass('muted');
  }

  function fireSwitch(e){
    e.preventDefault();
    var tab = $(this).parent().attr('id');
    var panel = $(this).attr('href');
    mute_all_tabs_but_this_one(tab);
    hide_all_panels_but_this_one(panel);
  }

  /*function hide_all_panels_but_this_one( id ){
    // $(".metro-trigger-" + id).addClass("active");
    // DOM.$metroTriggers.not(".metro-trigger-" + id).addClass("hidden");
    // DOM.$metroTargets.not(".cert-pathway-desc-" + id).addClass("hidden");
  }*/

  /* ===== public stuff ====== */

  // main init method
  function init(){
      cacheDom();
      bindEvents();
      setInitialState();
  }

  /* ===== export public methods ===== */
  
  return {
      init: init
  };

}());

jQuery(document).ready(function($){

  raceTabs.init();

});
