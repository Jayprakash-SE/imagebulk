$( function(){
    $("#addImages").on( 'click', function(){
        var catName = $("#categoryName").val();

        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": "Category:" + catName.replace("Category:", ""),
            "cmprop": "title",
            "cmnamespace": "6",
            "cmtype": "file",
            "cmlimit": "50",
            "origin": "*"
        }

        $.get(url="https://commons.wikimedia.org/w/api.php", params).done( function (data) {
            members = data.query.categorymembers
            cats = ""
            members.forEach(item => {
                cats += item.title + "\n";
            });
            $("#imageNameList").val(cats);
        })
    });
});
