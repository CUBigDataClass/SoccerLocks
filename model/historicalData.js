const sqlite3 = require('sqlite3').verbose();
var leagueArray = [];
var pushArray =[];
var processedArray =[];
var i =0;
var j =0; 

// open database
let db = new sqlite3.Database('database.sqlite', (err) => {
  if (err) {
  	console.log('here');
    return console.error(err.message);
  }
  console.log('Connected to the in-memory SQlite database.');
});

db.all("SELECT * FROM football_data", function(err, rows) {  
    rows.forEach(function (row) {
    	var nullCheck = row.B365H;
    	var homeShotCheck = row.HS;
    	var awayShotCheck = row.AS
    	//Filter out any unusable data containing Null Values
    	if(!nullCheck || !homeShotCheck || !awayShotCheck){  
        	// console.log(row.Date,row.HomeTeam, row.AwayTeam, row.FTR, row.B365H, row.B365D, row.B365A); 

        }
        else{
        	// Filter 
        	var rowValues = { Date: row.Date, League: row.Div, HomeTeam: row.HomeTeam, AwayTeam: row.AwayTeam, HomeOdds: row.B365H, DrawOdds: row.B365D, 
        		ayOdds: row.B365A, Result: row.FTR, HomeGoals: row.FTHG, AwayGoals: row.FTAG, HomeShots: row.HS, HomeTargets: row.HST, AwayShots: row.AS, 
        		AwayTargets: row.AST};
        	// console.log(row.Date,row.HomeTeam, row.AwayTeam, row.B365H, row.B365D, row.B365A, row.FTR, row.FTHG, row.FTAG, row.HS, row.HST, row.AS, row.AST);
        	pushArray.push(rowValues);
        }  
    })  
});

// close the database connection
db.close((err) => {
  if (err) {
    return console.error(err.message);
  }
  console.log('Close the database connection.');
  combineData();
  // pushMongo();
});

function combineData(){
  for (j=0; j<pushArray.length; j++){
		//State Counters, K is nested counter
		var counter=0;
		var k = j+1;

		//Initialize teams
		var homeTeam = pushArray[j].HomeTeam;
		var awayTeam = pushArray[j].AwayTeam;
		
		//Initialize Last 10 performance variables
		var homeWins = 0;
		var homeDraws = 0;
		var homeLosses =0;
		var homeGoals = 0;
		var homeOppGoals =0;
		var homeShots =0;
		var homeShotsTargets=0;
		var homeOppShots = 0;
		var homeOppShotsTargets=0; 

		var awayWins = 0;
		var awayDraws = 0;
		var awayLosses =0;
		var awayGoals = 0;
		var awayOppGoals =0;
		var awayShots =0;
		var awayShotsTargets=0;
		var awayOppShots = 0;
		var awayOppShotsTargets=0; 

		//While loop will exit once last 10 games have been analyzed for home and away team. Or if last 10 games of data is not available
		while (counter < 20 && k < 65158){
			//Check for last 10 games where home team played as  home team and away team played as away team. 
			if(homeTeam == pushArray[k].HomeTeam || awayTeam == pushArray[k].AwayTeam){
				//Cases where the home team played as the home team in a previous match
				if(homeTeam==pushArray[k].HomeTeam){
					//Add to last 10 game stats and results for home team 
					homeGoals = homeGoals + pushArray[k].HomeGoals;
					homeOppGoals = homeOppGoals + pushArray[k].AwayGoals;
					homeShots = homeShots + pushArray[k].HomeShots;
					homeShotsTargets = homeShotsTargets + pushArray[k].HomeTargets;
					homeOppShots = homeOppShots + pushArray[k].AwayShots;
					homeOppShotsTargets = homeOppShotsTargets + pushArray[k].AwayTargets;
					if(pushArray[k].Result == 'H'){
						homeWins = homeWins + 1;
					}
					else if(pushArray[k].Result == 'A'){
						homeLosses = homeLosses +1;
					}
					else{
						homeDraws= homeDraws +1;
					}
					counter++;
				}

				//Cases where the away team played as the away team in a previous matcth
				if(awayTeam==pushArray[k].AwayTeam){
					//Add to last 10 game stats and results for away team
					awayGoals = awayGoals + pushArray[k].AwayGoals;
					awayOppGoals = awayOppGoals + pushArray[k].HomeGoals;
					awayShots = awayShots + pushArray[k].AwayShots;
					awayShotsTargets = awayShotsTargets + pushArray[k].AwayTargets;
					awayOppShots = awayOppShots + pushArray[k].HomeShots;
					awayOppShotsTargets = awayOppShotsTargets + pushArray[k].HomeTargets;
					
					if(pushArray[k].Result == 'H'){
						awayLosses = awayLosses + 1;
					}
					else if(pushArray[k].Result == 'A'){
						awayWins = awayWins +1;
					}
					else{
						awayDraws= awayDraws +1;
					}
					counter++;
				}
				k++;
			}

			//Check for last 10 games where home team played as away team OR away team played as home team
		 	else if(homeTeam == pushArray[k].AwayTeam || awayTeam == pushArray[k].HomeTeam){
		 		//Cases where home team played as away team in previous match
				if(homeTeam == pushArray[k].AwayTeam){

					//Add to last 10 game stats and results for home team 
					homeGoals = homeGoals + pushArray[k].AwayGoals;
					homeOppGoals = homeOppGoals + pushArray[k].HomeGoals;
					homeShots = homeShots + pushArray[k].AwayShots;
					homeShotsTargets = homeShotsTargets + pushArray[k].AwayTargets;
					homeOppShots = homeOppShots + pushArray[k].HomeShots;
					homeOppShotsTargets = homeOppShotsTargets + pushArray[k].HomeTargets;
					if(pushArray[k].Result == 'A'){
						homeWins = homeWins + 1;
					}
					else if(pushArray[k].Result == 'H'){
						homeLosses = homeLosses +1;
					}
					else{
						homeDraws= homeDraws +1;
					}
					counter++;
				}

				//Cases where away team played as home team in previous match
				if(awayTeam == pushArray[k].HomeTeam){
					
					//Add to last 10 game stats and results for away team
					awayGoals = awayGoals + pushArray[k].HomeGoals;
					awayOppGoals = awayOppGoals + pushArray[k].AwayGoals;
					awayShots = awayShots + pushArray[k].HomeShots;
					awayShotsTargets = awayShotsTargets + pushArray[k].HomeTargets;
					awayOppShots = awayOppShots + pushArray[k].AwayShots;
					awayOppShotsTargets = awayOppShotsTargets + pushArray[k].AwayTargets;
					
					if(pushArray[k].Result == 'H'){
						awayWins = awayWins + 1;
					}
					else if(pushArray[k].Result == 'A'){
						awayLosses = awayLosses +1;
					}
					else{
						awayDraws= awayDraws +1;
					}
					counter++;
				}
				k++;
			}
		
			//If neither home team or away team played in the current row of data, simply increment counter
			else{
				k++;
			}
		}

	if(counter==20){
		var newHomeOdds = 1/pushArray[j].HomeOdds;
		var newAwayOdds = 1/pushArray[j].AwayOdds;
		var newDrawOdds = 1/pushArray[j].DrawOdds;
	  	var pValues= {result: pushArray[j].Result, oddsHome: newHomeOdds, oddsDraw: newDrawOdds, oddsAway: newAwayOdds, homeWins: homeWins, 
	  		homeDraws: homeDraws, homeLosses: homeLosses, homeGoals: homeGoals, homeOppGoals: homeOppGoals, homeShots: homeShots, 
	  		homeShotsTargets: homeShotsTargets, homeOppShots: homeOppShots, homeOppShotsTargets: homeOppShotsTargets, awayWins: awayWins, 
	  		awayDraws: awayDraws, awayLosses: awayLosses, awayGoals: awayGoals, awayOppGoals: awayOppGoals, awayShots: awayShots, 
	  		awayShotsTargets: awayShotsTargets, awayOppShots: awayOppShots, awayOppShotsTargets: awayOppShotsTargets};
	  		
	  	processedArray.push(pValues);
  	}
  }
  pushMongo()
}

function pushMongo(){
	var MongoClient = require('mongodb').MongoClient;
	var url = "mongodb://localhost:27017/soccerDB";

	MongoClient.connect(url, function(err, db) {
	  if (err) throw err;
	  var dbo = db.db("soccerDB");
	  var myobj = processedArray;
	  dbo.collection("processedDataNew").insertMany(myobj, function(err, res) {
	    if (err) throw err;
	    console.log("Number of documents inserted: " + res.insertedCount);
	    db.close();
	  });
	});
}