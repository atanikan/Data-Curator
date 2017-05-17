/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


var values = [ {hostname : "midway001.rcc.uchicago.edu"},
        {path : "/cds/rcc-staff"},
        {username : "atanikan"},
        {password : "tuxedo_picachu007"},
        {mode : "parent"}];
    
    
    $.ajax({
            method:'POST',
            url:'http://127.0.0.1:5000/getFancyInfo',
            dataType: "json",
            contentType: "application/json ; charset=utf-8",
            data: JSON.stringify(values),
            success: function(data){
                 console.log(data.listObjects);
                 $("#tree").fancytree({
                    checkbox: true,
                    selectMode: 3,
                    persist: {
                        expandLazy: false,
                        overrideSource: false,
                        store: "cookie", // force using cookies!
                    },
                    source: data.listObjects,
                    lazyLoad: function(event, data){
                        var node = data.node;
                        values[1]['path'] = node.key;
                        values[4]['mode'] = 'child';
                        data.result = $.ajax({
                        url:'http://127.0.0.1:5000/getFancyInfo',
                        method:'POST',
                        dataType: "json",
                        contentType: "application/json ; charset=utf-8",
                        data: JSON.stringify(values),
                        cache: false,
                        success: function (resp){
                            console.log(resp.listObjects);
                            node.addChildren(resp.listObjects);
                            node.fixSelection3AfterClick();
                            node.toggleExpanded();
                        }
                        });
                    },
                    select: function(event, data) {
            // Get a list of all selected nodes, and convert to a key array:
                    var selKeys = $.map(data.tree.getSelectedNodes(), function(node){
                      return node.key;
                    });
                    $("#echoSelection3").text(selKeys.join(", "));

                    // Get a list of all selected TOP nodes
                    var selRootNodes = data.tree.getSelectedNodes(true);
                    // ... and convert to a key array:
                    var selRootKeys = $.map(selRootNodes, function(node){
                      return node.key;
                    });
                    $("#echoSelectionRootKeys3").text(selRootKeys.join(", "));
                    $("#echoSelectionRoots3").text(selRootNodes.join(", "));
                  },
                    dblclick: function(event, data) {
                      data.node.toggleSelected();
                    },
                    keydown: function(event, data) {
                      if( event.which === 32 ) {
                        data.node.toggleSelected();
                        return false;
                      }
                    },
          // The following options are only required, if we have more than one tree on one page:
        //        initId: "SOURCE",
                    cookieId: "fancytree-Cb3",
                    idPrefix: "fancytree-Cb3-"
                });
            },
              failure: function(errMsg) {
                alert(JSON.stringify(errMsg.toString()));
            }
       });
    $("#btnToggleSelect").click(function(){
      $("#tree").fancytree("getRootNode").visit(function(node){
        node.toggleSelected();
      });
      return false;
    });
    $("#btnDeselectAll").click(function(){
      $("#tree").fancytree("getTree").visit(function(node){
        node.setSelected(false);
      });
      return false;
    });
    $("#btnSelectAll").click(function(){
      $("#tree").fancytree("getTree").visit(function(node){
        node.setSelected(true);
      });
      return false;
    });