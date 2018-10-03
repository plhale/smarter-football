"""
# NFL Passer Rating Formula
The NFL passer rating formula includes four variables:
    - completions percentages
    - yards per attempt
    - touchdowns per attempt
    - interception per attempt

Each of these variables is scaled to a value between 0 and 2.375, with 
1.0 being statistically average (based on league data between 1960-1970).

Note: passing performance in 2017 as the league average rating was 88.6

Source: https://en.wikipedia.org/wiki/Passer_rating 

"""

import pandas as pd

pass_ = pd.read_csv('pass_.csv')

qb_rating = pass_.groupby(['passer']).aggregate({
    'passing_cmp':sum,
    'passing_att':sum,
    'passing_yds':sum,
    'passing_tds':sum,
    'passing_int':sum
}).reset_index()

qb_rating['cmp'] = ((qb_rating.passing_cmp / qb_rating.passing_att) - .3) * 5           # completion percentage
qb_rating['ypa'] = ((qb_rating.passing_yds / qb_rating.passing_att) - 3) * .25          # yards per attempt
qb_rating['tdpa'] = (qb_rating.passing_tds / qb_rating.passing_att) * 20                # touchdowns per attempt 
qb_rating['intpa'] = 2.375 - ((qb_rating.passing_int / qb_rating.passing_att) * 25)     # interceptions per attempt 

rating_col = ['cmp', 'ypa', 'tdpa', 'intpa']

def pass_rate_quality_check(rating):
    """
    If the result of any calculation is greater than 2.375, it is set to 2.375. 
    If the result is a negative number, it is set to zero.
    """
    if rating > 2.375:
        rating = 2.375

    elif rating < 0:
        rating = 0
    
    return rating

qb_rating['cmp'] = qb_rating.cmp.apply(lambda x: pass_rate_quality_check(x))
qb_rating['ypa'] = qb_rating.ypa.apply(lambda x: pass_rate_quality_check(x))
qb_rating['tdpa'] = qb_rating.tdpa.apply(lambda x: pass_rate_quality_check(x))
qb_rating['intpa'] = qb_rating.intpa.apply(lambda x: pass_rate_quality_check(x))


# Passer Rating
qb_rating['pass_rate'] = ((qb_rating['cmp'] + qb_rating['ypa'] + qb_rating['tdpa'] + qb_rating['intpa']) / 6) * 100

print(qb_rating)

############################################################
"""
Here is the new function for qb_rating
"""
def qb_rating(row):    
    if row.PassAttempt == 0: return 0
    cmp_ = ((row.PassComplete / row.PassAttempt) - .3) * 5
    ypa_ = ((row['Yards.Gained'] / row.PassAttempt) - 3) * .25
    tdpa_ = ((row.Touchdown / row.PassAttempt) *20)
    intpa_ = 2.375 - ((row.InterceptionThrown / row.PassAttempt) * 25)
    
    cmp_ = pass_rate_quality_check(cmp_)
    ypa_ = pass_rate_quality_check(ypa_)
    tdpa_ = pass_rate_quality_check(tdpa_)
    intpa_ = pass_rate_quality_check(intpa_)
    
    rating = ((cmp_ + ypa_ + tdpa_ + intpa_) / 6 )* 100
    
    return rating 

# nfl['qb_rating'] = nfl.apply(qb_rating, axis=1)

#####
"""
Cumlative Passing Features

May need to consider the implications of doing a cummsum metrics on the current play, as it would 
indicate the result of the play not the prior. May need to consider shifting down stats afterwards.
"""

pass_['passing_att_cum'] = (pass_.groupby(['passer'])['passing_att'].cumsum())
pass_['passing_cmp_cum'] = (pass_.groupby(['passer'])['passing_cmp'].cumsum())
pass_['passing_int_cum'] = (pass_.groupby(['passer'])['passing_int'].cumsum())
pass_['passing_tds_cum'] = (pass_.groupby(['passer'])['passing_tds'].cumsum())
pass_['passing_yds_cum'] = (pass_.groupby(['passer'])['passing_yds'].cumsum())

pass_['cmp_cum'] = ((pass_.passing_cmp_cum / pass_.passing_att_cum) - .3) * 5           # completion percentage
pass_['ypa_cum'] = ((pass_.passing_yds_cum / pass_.passing_att_cum) - 3) * .25          # yards per attempt
pass_['tdpa_cum'] = (pass_.passing_tds_cum / pass_.passing_att_cum) * 20                # touchdowns per attempt 
pass_['intpa_cum'] = 2.375 - ((pass_.passing_int_cum / pass_.passing_att_cum) * 25)     # interceptions per attempt 

pass_['cmp_q'] = pass_.cmp_cum.apply(lambda x: pass_rate_quality_check(x))
pass_['ypa_q'] = pass_.ypa_cum.apply(lambda x: pass_rate_quality_check(x))
pass_['tdpa_q'] = pass_.tdpa_cum.apply(lambda x: pass_rate_quality_check(x))
pass_['intpa_q'] = pass_.intpa_cum.apply(lambda x: pass_rate_quality_check(x))

# Passer Rating

pass_['pass_rate_cum'] = ((pass_['cmp_q'] + pass_['ypa_q'] + pass_['tdpa_q'] + pass_['intpa_q']) / 6) * 100

pass_.drop(['cmp_cum', 'ypa_cum', 'tdpa_cum', 'intpa_cum','cmp_q','ypa_q','tdpa_q','intpa_q'], axis=1, inplace=True)



############################################################################################################################
# Success Rate Calculation [WORK IN PROGRESS]

"""
Per [Football Outsiders](http://www.footballoutsiders.com/stat-analysis/2004/introducing-running-back-success-rate), a run is 
considered a success if it satisfies the following benchmarks:

    1. Gains 40% of yards needed on first down, 60% of yards needed on second down, or 100% of yards needed on third down

    2. If the offense is behind by more than a touchdown in the fourth quarter, the first/second/third down benchmarks change 
    to 50%/65%/100%, respectively.

    3. If the offense is ahead by any amount in the fourth quarter, the first/second/third down benchmarks change to 30%/50%/100%, 
    respectively.
"""

def success_rate_cal(play):
    qtr = int(play.qtr)
    down = int(play.down)
    togo = int(play.ydstogo)
    first = int(play.first_down)
    att = int(play.play_attempt)
    yds = int(play.yards_gained)
    
    result = yds / att
    yards_obtained = yds / togo

    
    #if (play.down == 3) & (play.first_down == 0):
        # if play resulted in 4th down (unsuccessful attempt at 1st down)
     #   return 0 
    
    if down == 1:
        return 1
    
    elif down == 1:
        if yards_obtained >= .40:
            return yards_obtained
        
    elif down == 2:
        if yards_obtained >= .60:
            return yards_obtained
    
    elif down >= 3:
        if yards_obtained >= 1:
            return yards_obtained
    
    return down

#success_rate_cal(test_play)
