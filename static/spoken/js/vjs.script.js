/* Author:

*/


/* Video player START */
$generatePlayers = function () {
	var generatedPlayers = new Array();
	$(".video-js").each(function(){
				generatedPlayers.push($(this).attr('id'));
	});
	var aspectRatio = 264/640;
    // Catch each of the player's ready events and resize them individually
    // jQuery deferred might be a neater way to wait for ready on all components to load and avoid a bit of repetition
    for (var i = 0; i < generatedPlayers.length; i ++) {
        videojs('#' + generatedPlayers[i]).ready(function() {
            resizeVideoJS(this);
        });
    }

    // Loop through all the players and resize them
    function resizeVideos() {
        for (var i = 0; i < generatedPlayers.length; i ++) {
            var player = videojs('#' + generatedPlayers[i]);
            resizeVideoJS(player);
        }
    }

    // Resize a single player
    function resizeVideoJS(player){
        // Get the parent element's actual width
        var width = $(".videoContainerProtocol").innerWidth();

        // Set width to fill parent element, Set height
        player.width(width).height( width * aspectRatio );
    }
    window.onresize = resizeVideos;
};


$callMovies = function () {

$(".videoContainerProtocol").each(function ()
	{
	if (!$(this).hasClass("protocolsRun")) {
	$(this).addClass("protocolsRun");
	var number = 1 + Math.floor(Math.random() * 1000);

	$(this).click(function ()
	{

		var theID = $(this).find(".videoInfo").attr("data-video-id");
		var videoSRC = $(this).find(".videoInfo").attr("data-source-video");
		var posterSRC = $(this).find(".posterInfo").attr("src");

		$(this).append("<video id='"+theID+""+number+"' class='video-js vjs-default-skin' controls='' preload='auto' poster='"+posterSRC+"' data-setup='{}'><source src='"+videoSRC+"' type='video/mp4'></source></video>");

		$(this).find(".playButtonContainer").remove();
		$(this).find(".videoInfo").remove();
		$(this).find(".posterInfo").remove();
		$(this).unbind('click');



		/* Generate players through videojs START */
    	$generatePlayers();
		/* Generate players through videojs END */


		/* Let the player start START */
		var myPlayer = videojs(""+theID+""+number+"");
		myPlayer.play();
		/* Let the player start END */

        });
    }
	});

};
/* Video player END */







$(document).ready(function () {
	$callMovies();
	$("#loadInMovieButton").click(function (e)
	{
		e.preventDefault();
  	});
});
