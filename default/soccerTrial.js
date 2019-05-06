const http = require('http');
var fs = require('fs');

const jsdom = require("jsdom");
const { JSDOM } = jsdom;
var recent;

var Real = "https://lh3.googleusercontent.com/7m9PWXxmcH_s6Rg8bzm8xq-KuOXOGW-ncPG-uEbzBNR6r2uC-1tFtCg04KbKT_fPwom2QMo_znwtYgTxUznTS1BYnHmdNrHfDQ3NTLCuDrpHMel9sOolbAWhBECxEKlS3BvvVqHdlA=w2400";

var i=1;

var express = require('express')
var app = express()
var info = [];

app.use(express.static('img'))
app.get('/', function (req, res) {
	const MongoClient = require('mongodb').MongoClient;
	const uri = "mongodb+srv://joeycris97:chester!11@matchdb-volt6.gcp.mongodb.net/test?retryWrites=true";
	const client = new MongoClient(uri, { useNewUrlParser: true });
  	var monthNames = [
    "January", "February", "March",
    "April", "May", "June", "July",
    "August", "September", "October",
    "November", "December"
  	];
  	var today = new Date();
 	var day = today.getDate();
  	var monthIndex = today.getMonth();
  	var year = today.getFullYear();

  	var date =  monthNames[monthIndex] + ' '+ day  + ' ' + year;

  	// var dateCheck = today.getFullYear()+'-0'+(today.getMonth()+1)+'-0'+(today.getDate()-1);

	//FIX THIS

	client.connect(err => {
	  const collection = client.db("matchdb").collection("matchmaster");
	  // const collection2 = client.db("matchdb").collection("matchmaster");
	     collection.find().sort({match_date:-1}).limit(1).toArray(function(err,result) {
	     		var recent = result[0].match_date;
	     		collection.find({match_date: recent }).toArray(function(err,data){
	     			formatResults(data,date);
	     			client.close();
	     		});
	     		client.close();
	     	});
	});


	function formatResults(input){
		var array=input;
		var todaysDate = date;
		if(array!=''){
		JSDOM.fromFile("soccerLocks.html", "text/html").then(dom => {
		let window = dom.window,
	    document = window.document;

	    var todaysGames = document.getElementById('todaysGames');

	    var h3 = document.createElement("H3");
		h3.setAttribute("id","games");

	    h3.innerHTML= "Displaying Game Predictions For: " + array[0].match_date;
	    todaysGames.append(h3);
		for(i=0;i<array.length;i++){
		    var results = document.getElementById('results');
		    var home_team = array[i].home_team;
		    var away_team = array[i].away_team;
		    var date = array[i].match_date;

		    var model_home = array[i].model_home;
		    var model_draw= array[i].model_draw;
		    var model_away = array[i].model_away;

		    var display_home = (1/model_home);
		    var homeFinal = display_home.toFixed(2);
		   	var display_draw = (1/model_draw);
		    var drawFinal = display_draw.toFixed(2);
			var display_away = (1/model_away);
		    var awayFinal = display_away.toFixed(2);

		    var book_home = 1/array[i].home_odds;
		    var book_draw = 1/array[i].draw_odds;
		    var book_away = 1/array[i].away_odds;

		    var home_difference = model_home - book_home;
		    var draw_difference = model_draw - book_draw;
		    var away_difference = model_away - book_away;

		    var homeDif = (home_difference*100).toFixed(2);
		    var drawDif = (draw_difference*100).toFixed(2);
		    var awayDif = (away_difference*100).toFixed(2);


			var difDisplayHome = "<p><span> Percent Difference: " + homeDif + "%</span>";
			var difDisplayDraw = "<span> Percent Difference: " + drawDif + "%</span>";
			var difDisplayAway = "<span> Percent Difference: " + awayDif + "%</span></p>"


		    if (homeDif>2){
		    	difDisplayHome = "<p><span id='special'> Percent Difference: " + homeDif + "%</span>"
		    }   

		    if (drawDif >2){
				difDisplayDraw = "<span id='special'> Percent Difference: " + drawDif + "%</span>"		    
			}   

		    if(awayDif>2){
		    	 difDisplayAway = "<span id='special'> Percent Difference: " + awayDif + "%</span></p>"	
		    }
	
			var imageHome = home_team + ".png";
			var imageAway = away_team + ".png";

			if(home_team == "Brighton &amp; Hove Albion")
			{
				var image1 = "<img src = 'Brighton.png' id = 'home' alt = 'Brighton & Hove Albion'>"
				var image2 = "<img src = '" + imageAway + "' id = 'away' alt = 'Home Team'>";
			}
			else if(away_team == "Brighton &amp; Hove Albion")
			{
				var image2 = "<img src = 'Brighton.png' id = 'away' alt = 'Brighton & Hove Albion'>"
				var image1 = "<img src = '" + imageHome + "'id = 'home' alt = 'Home Team'>";
			}
			else {
				var image1 = "<img src = '" + imageHome + "' id = 'home' alt = 'Home Team'>";
				var image2 = "<img src = '" + imageAway + "' id = 'away' alt = 'Home Team'>";

			}

			var details = "<h2 id = 'matchDetails'>" + home_team + " vs " + away_team + "</h2>";
			var finalDetails = "<div id = 'details'>" + details + "</div>";

			var finalImage = "<div id='photos'>" + image1 + finalDetails + image2 + "</div>"

		    if(home_difference){


		    var div = document.createElement("DIV");
		    div.setAttribute("id","match");
		    // var matchCard = document.getElementById(home_team);

		    var teamInfo = "<div id='lastThing'><p id='homeTag'> Home </p><p id ='awayTag'> Away </p></div>" 
		    var headers = "<h2><span id>" + home_team + " Odds to Win </span><span id='centerMe'> Odds of Draw </span><span>" + away_team + " Odds to Win </span></h2>";
		    var odds="<p><span> Sportsbook Odds: " + array[i].home_odds + "  </span><span>Sportsbook Odds: " + array[i].draw_odds + "</span><span>Sportsbook Odds: " + array[i].away_odds +"</span></p>";
		    var ourOdds="<p><span> Soccer Locks Odds: " + homeFinal + "  </span><span>Soccer Locks Odds: " + drawFinal+ "</span><span>Soccer Locks Odds: " + awayFinal +"</span></p>";
		    var percentEdge = difDisplayHome + difDisplayDraw + difDisplayAway;

		    // div.innerHTML = "<ul><li> Time: " + n + "  </li> " + "<li>Home Team: " + home_team + "   Away Team: " + away_team + "<li> Home Difference: " + home_difference + "</li><li> Draw Difference: " + draw_difference +"</li><li> Away Difference: " + away_difference + "</li></ul><br><br>";
		    div.innerHTML=teamInfo + finalImage + headers + odds + ourOdds +percentEdge;
		    results.append(div);
		    var something = dom.serialize()

			}

		}
		res.writeHead(200, {'Content-Type': 'text/html'});
		res.write(something);
		res.end();
		});
	}

	else{
		JSDOM.fromFile("soccerLocks.html", "text/html").then(dom => {
		let window = dom.window,
	    document = window.document;

		var results = document.getElementById('results');
	    var div = document.createElement("DIV");
		div.setAttribute("id","noMatch");
		div.innerHTML = "<h3 id='games'> There are no games today, please check back tomorrow.</h3>";
		results.append(div);
		var something = dom.serialize();
		res.writeHead(200, {'Content-Type': 'text/html'});
		res.write(something);
		res.end();
		});		
	}
	}
})
app.listen(8080)

