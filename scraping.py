from lxml import html
import requests

map_pool = ["dust2", "inferno", "mirage", "cache", "nuke", "overpass", "cobblestone"]

def get_percentage(team1, team2):

    page = requests.get('http://www.csgonuts.com/history?t1=%s&t2=%s' % (team1, team2))
    tree = html.fromstring(page.text)
    if "have no record" in tree.xpath('/html/body/div/div[2]/div[1]/div[2]/div/text()[1]')[0]:
        return "No matches"

    results_amount = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[3]/div/div[1]/p[1]/span/text()')
    results_percentage = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[3]/div/div[1]/p[2]/span/text()')
    return results_percentage + results_amount

def footnote(reply, team1, team2):
    reply += "\n\n----\n\n^This ^is ^a ^bot ^made ^by ^[/u/TreSxNine](http://www.reddit.com/user/TreSxNine/) ^that ^uses ^[CSGOnuts.com](http://www.csgonuts.com/) ^to ^gather ^information ^about ^team ^matchups." \
             "\n\n^Call ^it ^by ^using ^'Statbot! ^[\*Whatever\*] ^[team1] ^vs ^[team2] ^[\*Whatever\*] ^[map ^\(optional\)]'." \
             "\n\n[^[Report ^a ^bug]](http://www.np.reddit.com/message/compose/?to=tresxnine&amp;subject=CSGOnutsStatsBot)"
    if team1 != "" and team2 != "":
        reply += " [^[Source]](http://www.csgonuts.com/history?t1=%s&t2=%s)" % (team1, team2)
    return reply

def mapformat(map):
    map = map.replace("'", "").replace(".", "").replace("de_", "").replace(",", "")
    map = map.lower()
    return map

def team_format(team):
    team = team.replace("'", "").replace(".", "")
    team = team.lower()
    if team == "navi" or team == "natusvincere":
        team = "NatusVincere"
    if team == "teamsolomid" or team == "tsm":
        team = "TSM"
    if team == "mouz" or team == "mousesports":
        team = "Mousesports"
    if team == "envy us" or team == "envy" or team == "envyus":
        team = "EnVyUs"
    if team == "g2" or team == "gamers2":
        team = "Gamers2"
    if team == "luminositygaming" or team == "lg" or team == "luminosity":
        team = "Luminosity"
    if team == "vp" or team == "virtuspro" or team == "virtus.pro":
        team = "Virtus.Pro"
    if team == "alientechblack" or team == "alientech.black":
        team = "AlienTech.Black"
    if team == "netcodeguides" or team == "netcodeguidescom" or team == "NetcodeGuides.com":
        team = "NetcodeGuides.com"
    if team == "alientechblue" or team == "alientech.blue":
        team = "AlienTech.Blue"
    if team == "keyd" or team == "keydstars":
        team = "KeydStars"
    if team == "nihilium" or team == "nihilum":
        team = "Nihilum"
    if team == "vox" or team == "voxeminor":
        team = "VoxEminor"
    if team == "winoutnet" or team == "winout":
        team = "WinOut.net"
    return team

def get_maps(team1, team2, map_choice):

    map_choice = mapformat(map_choice)
    page = requests.get('http://www.csgonuts.com/history?t1=%s&t2=%s' % (team1, team2))
    tree = html.fromstring(page.text)
    map_dict = {}

    for i in range(0, 15):
        map_name = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[3]/div/div[%s]/div[1]/a/span/text()' % i)
        percentage = tree.xpath('/html/body/div/div[2]/div[2]/div[2]/div[3]/div/div[%s]/div[2]/span/text()' % i)
        try:
            map_dict[map_name[0]] = percentage[0]
        except IndexError:
            pass
    return map_dict[map_choice]

def message_deconstructor(pbody):
    return_dict = {}
    post_body_split = pbody.split()

    for wordindex in range(0, len(post_body_split)):
        if not "vs" in post_body_split:
            return_dict['vs_error'] = "Incorrect formatting. Missing 'vs'"
            return return_dict
        if post_body_split[wordindex] == "vs":
            try:
                return_dict['team1'] = team_format(post_body_split[wordindex-1])
                return_dict['team2'] = team_format(post_body_split[wordindex+1])
                if return_dict['team1'] == return_dict['team2']:
                    return_dict['error'] = "A team versus itself? That would be a fight to watch!"
                    return return_dict
                return_dict['global_percentage'] = get_percentage(return_dict['team1'], return_dict['team2'])

                if return_dict['global_percentage'] == "No matches":
                    return_dict['team_error'] = "No record of %s vs %s. [Check for yourself](http://www.csgonuts.com/history?t1=%s&t2=%s)" % (return_dict['team1'], return_dict['team2'], return_dict['team1'], return_dict['team2'])
                    return return_dict

                if return_dict['global_percentage'] == []:
                    return_dict['team_error'] = "Can't find one or two teams. Keep in mind that you can't use spaces in " \
                                                "team names. If you think this is faulty, please contact me."
                    return return_dict
            except IndexError:
                return_dict['error'] = "Invalid request! Either this is a very rare error saying that there are no recorded " \
                                       "matches between these two teams, or you formatted the command incorrectly (less likely)" \
                                       ""
                return return_dict
                pass
            except KeyError:
                return_dict['error'] = "Invalid request! Either this is a very rare error saying that there are no recorded" \
                                       "matches between these two teams, or you formatted the command incorrectly (less likely)" \
                                       ""
                return return_dict
                pass

        if mapformat(post_body_split[wordindex]) in map_pool:
            map = mapformat(post_body_split[wordindex])
            try:
                return_dict['map_percentage'] = get_maps(return_dict['team1'], return_dict['team2'], map)
                return_dict['map_name'] = map
            except IndexError:
                return_dict['error'] = "Invalid request! Either this is a very rare error saying that there are no recorded" \
                                       "matches between these two teams, or you formatted the command incorrectly (less likely)" \
                                       ""
                return return_dict
                pass
            except KeyError:
                return_dict['map_error'] = "No records of %s vs %s on %s. " % (return_dict['team1'], return_dict['team2'], map + "[Check for yourself](http://www.csgonuts.com/history?t1=%s&t2=%s)" % (return_dict['team1'], return_dict['team2']))
                return return_dict
                pass

    return return_dict

def bot_reply(pbody):
    team_dict = message_deconstructor(pbody)

    if 'vs_error' in team_dict:
        return footnote(team_dict['vs_error'], "", "")
    elif 'team_error' in team_dict:
        return footnote(team_dict['team_error'], "", "")
    elif 'map_error' in team_dict:
        return footnote(team_dict['map_error'], team_dict['team1'], team_dict['team2'])
    elif 'error' not in team_dict:
        if 'map_percentage' in team_dict:
            reply_to_reddit = team_dict['map_percentage'] + ' on ' + team_dict['map_name'] + "."
        else:
            reply_to_reddit = team_dict['global_percentage'][0] + " (" + team_dict['global_percentage'][1] + ")."
    else:
        return footnote(team_dict['error'], "", "")
    return footnote(reply_to_reddit, team_dict['team1'], team_dict['team2'])

print bot_reply("Statbot! Give us nip vs navi on de_Mirage.")


