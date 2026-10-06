"""Season 1 Vancouver filming locations: raw rows compiled from the location managers' book
"X Marks the Spot" (Gradnitzer & Pittson, 1999) and IMDb per-episode listings.
Row: ep, title, name, address, city, played, sources (B=book, I=IMDb, W=Wikipedia), confidence, note, geocode query."""
B, I, W = "book", "imdb", "wiki"
ROWS = [
# --- Pilot
("1X79","Pilot","Queen Elizabeth Park","Cambie St & W. 33rd Ave","Vancouver","Bellefleur graveyard, where the coffin is exhumed",[B],"high","The first of many graveyard sets filmed in this park.","Queen Elizabeth Park, Vancouver, BC"),
("1X79","Pilot","Riverview Hospital (Crease Clinic and West Lawn)","2601 Lougheed Hwy","Coquitlam","Raymon County State Psychiatric Hospital: Crease Clinic interiors, West Lawn exterior",[B,I],"high","Production records give the site as 500 Lougheed Hwy, Port Coquitlam.","Riverview Hospital, Coquitlam, BC"),
("1X79","Pilot","Knowledge Network","4344 Mathissi Pl","Burnaby","FBI boardroom and the Pentagon warehouse",[B],"high",None,"4355 Mathissi Place, Burnaby, BC"),
("1X79","Pilot","CBC Vancouver","700 Hamilton St","Vancouver","FBI bullpen, Mulder's basement office and the FBI hallway",[B],"high","Production records print the address as 800 Hamilton St.","CBC, 700 Hamilton Street, Vancouver, BC"),
("1X79","Pilot","Seymour Demonstration Forest","Lillooet Rd (now Lower Seymour Conservation Reserve)","North Vancouver","The Oregon forest",[B],"high",None,"Lower Seymour Conservation Reserve, North Vancouver, BC"),
("1X79","Pilot","Cedar Lane Motel","926 160 St","Surrey (White Rock border)","The rural motel that burns",[B],"high",None,"926 160 Street, Surrey, BC"),
("1X79","Pilot","B.C. Hydro headquarters","333 Dunsmuir St","Vancouver","FBI lobby and Scully's laboratory",[B],"high",None,"333 Dunsmuir Street, Vancouver, BC"),
("1X79","Pilot","Scully's first apartment","610 Jervis St","Vancouver","Exterior of Scully's apartment",[B],"high","Used for the Pilot and Squeeze, then dropped for a building on Pendrell St.","610 Jervis Street, Vancouver, BC"),
# --- Deep Throat
("1X01","Deep Throat","Boundary Bay Airport","Airport Rd & 80th St (checkpoint); 7800 Alpha Way","Delta","Ellens Air Base: checkpoint, runway and hangar",[B],"high",None,"Boundary Bay Airport, Delta, BC"),
("1X01","Deep Throat","Hilltop Café","23904 Fraser Hwy","Langley","Flying Saucer Diner",[B,I],"high","another listing gives 23838 Fraser Hwy.","23904 Fraser Highway, Langley, BC"),
("1X01","Deep Throat","The Meat Market","1 W. Cordova St","Vancouver (Gastown)","Dunaway's Pub, where Deep Throat first approaches Mulder",[B,I],"high",None,"1 West Cordova Street, Vancouver, BC"),
("1X01","Deep Throat","Beach Grove Motel","5946 12 Ave","Delta (Tsawwassen)","Gateway Motor Lodge",[B,I],"high","Street number from a second listing.","5946 12 Avenue, Delta, BC"),
# --- Squeeze
("1X02","Squeeze","1000-block West Hastings Street","1000-block W. Hastings St","Vancouver","\"Calvert Street\": the drainage grate Tooms watches from, and the office above",[B],"high",None,"1050 West Hastings Street, Vancouver, BC"),
("1X02","Squeeze","Rear of Ideal Gift and Toy","51–53 W. Hastings St (rear)","Vancouver","Exterior of 66 Exeter Street, Tooms's building",[B],"high","Interiors were shot in an empty boarding house above the Meat Market, 1 W. Cordova St.","53 West Hastings Street, Vancouver, BC"),
("1X02","Squeeze","VPC Parkade","107 E. Cordova St","Vancouver","Underground parkade where Tooms attacks Usher",[B],"high",None,"107 East Cordova Street, Vancouver, BC"),
("1X02","Squeeze","Scully's first apartment","610 Jervis St","Vancouver","Exterior of Scully's apartment",[B,I],"high","another listing gives 611 Jervis St.","610 Jervis Street, Vancouver, BC"),
("1X02","Squeeze","Riverview Hospital","2601 Lougheed Hwy","Coquitlam","Scene not specified by the source",[I],"med",None,"Riverview Hospital, Coquitlam, BC"),
# --- Conduit
("1X03","Conduit","East Hastings Street","10 E. Hastings St","Vancouver","Scene not specified by the source",[I],"med",None,"10 East Hastings Street, Vancouver, BC"),
("1X03","Conduit","St. Edwards Drive","10469 St. Edwards Dr","Richmond","Scene not specified by the source",[I],"med",None,"10469 St. Edwards Drive, Richmond, BC"),
("1X03","Conduit","Burrard Street","664 Burrard St","Vancouver","Scene not specified by the source",[I],"med",None,"664 Burrard Street, Vancouver, BC"),
("1X03","Conduit","Vancouver Art Gallery","750 Hornby St","Vancouver","Scene not specified by the source",[I],"med",None,"750 Hornby Street, Vancouver, BC"),
# --- The Jersey Devil
("1X04","The Jersey Devil","900-block Station Street","900-block Station St","Vancouver","Atlantic City back streets: vacant building, restaurant exterior and police parking lot",[B,I],"high","another listing gives 1000 Station St.","950 Station Street, Vancouver, BC"),
("1X04","The Jersey Devil","Pacific Central Station","1150 Station St","Vancouver","Exterior of the Atlantic City Police Department",[I],"med",None,"1150 Station Street, Vancouver, BC"),
("1X04","The Jersey Devil","Twin Bridges, Seymour Demonstration Forest","Twin Bridges, Lower Seymour Conservation Reserve","North Vancouver","New Jersey woods and the creature's cave",[B],"high",None,"Twin Bridges, Lower Seymour Conservation Reserve, North Vancouver, BC"),
("1X04","The Jersey Devil","Angus Drive mansion","1451 Angus Dr","Vancouver (Shaughnessy)","Townhouse interior, the restaurant where Scully has her date, and Rob's office",[B],"high","The same house returned as the English estate in Fire.","1451 Angus Drive, Vancouver, BC"),
# --- Shadows
("1X05","Shadows","Lauren Kyte's house","858 E. 15th Ave","Vancouver","Lauren Kyte's house",[I,B],"high","Production records place Lauren's house in East Vancouver without the number.","858 East 15th Avenue, Vancouver, BC"),
("1X05","Shadows","Crease Clinic, Riverview Hospital","2601 Lougheed Hwy","Coquitlam","Bethesda Naval Hospital",[I],"med",None,"Riverview Hospital, Coquitlam, BC"),
("1X05","Shadows","Mountain View Cemetery","Fraser St & E. 39th Ave","Vancouver","Cemetery scene",[I],"med","The listing gives the intersection, which is the cemetery's corner.","Mountain View Cemetery, Vancouver, BC"),
# --- Ghost in the Machine
("1X06","Ghost in the Machine","Metrotower II","4720 Kingsway","Burnaby","Eurisko building: plaza, lobby and the tower lighting up floor by floor",[B],"high",None,"4720 Kingsway, Burnaby, BC"),
("1X06","Ghost in the Machine","Burnaby Public Library and Central Park","6100 Willingdon Ave","Burnaby","Parkade and office interiors; the day began in Central Park",[B],"med","Production records name the library parkade and administration area; street address looked up.","Bob Prittie Metrotown Library, Burnaby, BC"),
("1X06","Ghost in the Machine","Kingsborough Street","4517 Kingsborough St","Burnaby","Scene not specified by the source",[I],"med",None,"4517 Kingsborough Street, Burnaby, BC"),
# --- Ice
("1X07","Ice","Delta Air Park","4187 104 St","Delta","Doolittle Airfield, Nome, Alaska",[B,I],"high","another listing gives 4108 104 St. The research station interior was a set at the Molson Brewery stages.","Delta Heritage Air Park, Delta, BC"),
# --- Space
("1X08","Space","Canadian Airlines Operations Centre","6001 Grand McConachie Way","Richmond","Johnson Space Center simulator, ship corridor and hangar",[B],"high",None,"6001 Grant McConachie Way, Richmond, BC"),
("1X08","Space","Robson Square Conference Centre","800 Robson St","Vancouver","Mission control",[B,I],"high","Production records print 600 Robson St; another listing gives Howe & Robson.","Robson Square, Vancouver, BC"),
("1X08","Space","Sutton Place Hotel, room 1256","845 Burrard St","Vancouver","Belt's Pasadena bedroom in 1973",[B],"high","The fall was shot from a construction crane at the Wall Centre next door.","845 Burrard Street, Vancouver, BC"),
("1X08","Space","Mountain View Cemetery","Fraser St & E. 39th Ave","Vancouver","Scene not specified by the source",[I],"med",None,"Mountain View Cemetery, Vancouver, BC"),
# --- Fallen Angel
("1X09","Fallen Angel","Simon Fraser University","8888 University Dr","Burnaby","Washington park and plaza where Mulder meets Deep Throat",[B,I],"high",None,"Simon Fraser University, Burnaby, BC"),
("1X09","Fallen Angel","B.C. Hydro system control centre","Burnaby Mountain","Burnaby","Microwave station",[B],"med","Records give no street address.","Burnaby Mountain, Burnaby, BC"),
("1X09","Fallen Angel","Seymour Demonstration Forest gravel pit","Lower Seymour Conservation Reserve","North Vancouver","UFO crash site",[B],"high",None,"Lower Seymour Conservation Reserve, North Vancouver, BC"),
("1X09","Fallen Angel","Burrard Dry Dock","Foot of Lonsdale Ave","North Vancouver","Lake Michigan waterfront",[I],"med",None,"Burrard Dry Dock Pier, North Vancouver, BC"),
("1X09","Fallen Angel","Marine Drive","2036 Marine Dr","North Vancouver","Scene not specified by the source",[I],"med",None,"2036 Marine Drive, North Vancouver, BC"),
# --- Eve
("1X10","Eve","Seacrest Motel","864 Stayte Rd","White Rock","Lighthouse Motel",[B,I],"high","Production records print 864 Stayte Ave; another listing gives 862 Stayte Rd.","864 Stayte Road, White Rock, BC"),
("1X10","Eve","White Rock Sunset Café","15782 Marine Dr","White Rock","Roadside diner with the trucks parked outside",[B,I],"high","another listing gives 15773 Marine Dr.","15782 Marine Drive, White Rock, BC"),
("1X10","Eve","Orwell Street","12 Orwell St","North Vancouver","Scene not specified by the source",[I],"med",None,"12 Orwell Street, North Vancouver, BC"),
("1X10","Eve","Riverview Hospital","2601 Lougheed Hwy","Coquitlam","Scene not specified by the source",[I],"med",None,"Riverview Hospital, Coquitlam, BC"),
# --- Fire
("1X11","Fire","Hotel Vancouver","900 W. Georgia St","Vancouver","Venable Plaza Hotel: the drive-up, mezzanine and hallway",[B,I],"high","The fire itself was a set built to match the hotel.","900 West Georgia Street, Vancouver, BC"),
("1X11","Fire","Angus Drive mansion","1451 Angus Dr","Vancouver (Shaughnessy)","English country estate exterior",[B],"high",None,"1451 Angus Drive, Vancouver, BC"),
("1X11","Fire","Deerholme","6110 Price St","Burnaby","The Marsdens' rented house on Cape Cod",[I],"med",None,"6110 Price Street, Burnaby, BC"),
# --- Beyond the Sea
("1X12","Beyond the Sea","Garry Point Park","12011 7th Ave (foot of Chatham St)","Richmond (Steveston)","Shore where Scully's father's ashes are scattered",[B],"high",None,"Garry Point Park, Richmond, BC"),
("1X12","Beyond the Sea","Britannia Heritage Shipyard","5180 Westwater Dr","Richmond (Steveston)","Boathouse",[B],"high","Production records print the address as 12451 Westwater Dr.","Britannia Shipyards National Historic Site, Richmond, BC"),
("1X12","Beyond the Sea","Ramada Hotel","435 W. Pender St","Vancouver","Niagara Hotel",[I],"med",None,"435 West Pender Street, Vancouver, BC"),
("1X12","Beyond the Sea","Waterfront Station","601 W. Cordova St","Vancouver","The stone angel",[I],"med",None,"601 West Cordova Street, Vancouver, BC"),
# --- Gender Bender
("1X13","Gender Bender","Rowlatt Historic Farm","Campbell Valley Regional Park","Langley","The Kindred's commune",[B,I],"high",None,"Rowlatt Farmstead, Campbell Valley Regional Park, Langley, BC"),
("1X13","Gender Bender","Marine Grocery","3680 Moncton St","Richmond (Steveston)","General store and feed store in the Kindred's town",[B,I],"high",None,"3680 Moncton Street, Richmond, BC"),
("1X13","Gender Bender","Alexander Street","52 Alexander St","Vancouver (Gastown)","Scene not specified by the source",[I],"med",None,"52 Alexander Street, Vancouver, BC"),
# --- Lazarus
("1X14","Lazarus","Bank of Montreal","500–520 Granville St","Vancouver","Bank where Willis and Dupre are shot",[B],"high",None,"520 Granville Street, Vancouver, BC"),
("1X14","Lazarus","Orange Hall","341 Gore Ave","Vancouver","Apartment basement and the alley",[B,I],"high",None,"341 Gore Avenue, Vancouver, BC"),
("1X14","Lazarus","Riverview Hospital","2601 Lougheed Hwy","Coquitlam","Scene not specified by the source",[I],"med",None,"Riverview Hospital, Coquitlam, BC"),
# --- Young at Heart
("1X15","Young at Heart","Henry Birks & Sons","Granville St & W. Georgia St","Vancouver","Jewellery store robbery scene in the teaser",[B],"med","Production records name the store, with the Hudson's Bay building visible behind; it gives no street number.","Granville Street and West Georgia Street, Vancouver, BC"),
("1X15","Young at Heart","Orpheum Theatre","601 Smithe St","Vancouver","Concert hall",[I],"med",None,"601 Smithe Street, Vancouver, BC"),
("1X15","Young at Heart","Vancouver Art Gallery","750 Hornby St","Vancouver","Courtroom",[I],"med",None,"750 Hornby Street, Vancouver, BC"),
("1X15","Young at Heart","Pacific Central Station","1150 Station St","Vancouver","Scene not specified by the source",[I],"med",None,"1150 Station Street, Vancouver, BC"),
("1X15","Young at Heart","Jones Avenue","1640 Jones Ave","North Vancouver","Scene not specified by the source",[I],"med",None,"1640 Jones Avenue, North Vancouver, BC"),
# --- E.B.E.
("1X16","E.B.E.","TRIUMF","4004 Wesbrook Mall, UBC","Vancouver","Exterior of the power plant where the alien is held",[B],"high",None,"TRIUMF, 4004 Wesbrook Mall, Vancouver, BC"),
("1X16","E.B.E.","Powertech Labs","12388 88 Ave","Surrey","Interior of the facility",[B,I],"high",None,"12388 88 Avenue, Surrey, BC"),
# --- Miracle Man
("1X17","Miracle Man","Reverend Hartley's house","24990 River Rd","Langley (Fort Langley)","Reverend Hartley's estate",[B,I],"high",None,"24990 River Road, Langley, BC"),
("1X17","Miracle Man","Riverview Hospital","2601 Lougheed Hwy","Coquitlam","Scene not specified by the source",[I],"med",None,"Riverview Hospital, Coquitlam, BC"),
# --- Shapes
("1X18","Shapes","Bordertown","224th St","Maple Ridge","The reservation: town, police office, morgue, bar and Ish's house",[B,I],"high","A western town built for filming; records give the street only.","224 Street and 132 Avenue, Maple Ridge, BC"),
# --- Darkness Falls
("1X19","Darkness Falls","Lighthouse Park","4902 Beacon Ln","West Vancouver","Logging camp and cabins",[B,I],"high",None,"Lighthouse Park, West Vancouver, BC"),
("1X19","Darkness Falls","Seymour Demonstration Forest","Lower Seymour Conservation Reserve","North Vancouver","Sawmill office and the logging road",[B],"high",None,"Lower Seymour Conservation Reserve, North Vancouver, BC"),
# --- Tooms
("1X20","Tooms","City Square Mall","555 W. 12th Ave","Vancouver","Mall with the escalator where Tooms dies; the FBI plaza is the steps to the north",[B],"high",None,"555 West 12th Avenue, Vancouver, BC"),
# --- Born Again
("1X21","Born Again","Riverview Hospital","2601 Lougheed Hwy","Coquitlam","Scene not specified by the source",[I],"med",None,"Riverview Hospital, Coquitlam, BC"),
# --- The Erlenmeyer Flask
("1X23","The Erlenmeyer Flask","Vanterm overpass","Clark Dr at the port","Vancouver","Bridge where Mulder is exchanged and Deep Throat is shot",[B],"high","The high master shot was taken from the grain elevators next door.","Clark Drive and Stewart Street, Vancouver, BC"),
("1X23","The Erlenmeyer Flask","The Wellington","2630 York Ave","Vancouver (Kitsilano)","Exterior of Mulder's apartment building",[B,I],"high","another listing gives 2644 York Ave.","2630 York Avenue, Vancouver, BC"),
("1X23","The Erlenmeyer Flask","Open Learning Agency","4355 Mathissi Pl","Burnaby","Pentagon warehouse",[B],"high","The same warehouse used in the Pilot.","4355 Mathissi Place, Burnaby, BC"),
("1X23","The Erlenmeyer Flask","Sanderson Way","4490 Sanderson Way","Burnaby","Scene not specified by the source",[I],"med",None,"4490 Sanderson Way, Burnaby, BC"),
]
