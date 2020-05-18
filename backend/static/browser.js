var VueComponent = new Vue({
    el: "#vue-entry",
    data: {
        previewOn: false,
        imageURL: "",
    },
    methods: {
        insertGraph: function(idx) {
            this.imageURL =  "/getPreview/" + idx.toString();
            this.id = idx;
            this.previewOn = true;
        }, 
        getRoadHistory: function(){
            "/getRoadHistory/" + id.toString();
        }
    }
})