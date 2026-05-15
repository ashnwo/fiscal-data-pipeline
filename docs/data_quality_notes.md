# Findings - Treasury_debt data 
- 8,307 distinct dates over 33 years = ~252/year average. The federal government has 250–260 operational days per year, so this data is represented daily.
- Consistent coverage between 1993 and 2026. ~250 rows per year. 
- 2 anomolies in gap days. Both Dec 31, 1997 and Feb 2, 2000 both have a gap of 5 days until the next entry in the data. 
    - 3 Days = a standard weekend
    - 4 Days = a holiday weekend
- Data collection by the Treasury started in April 1993. All analysis will either exclude 1993 or treat it as a partial year.   

- debt_held_public_amt, intragov_hold_amt only populated from ~2006 onward. 
- tot_pub_debt_out_amt (total debt) populated throughout the 33 years in full. 
- Sparse pre-2006 populated rows 

- From 1997 -> 2001 = 1 row per year on Sept. 30th (end of the fiscal year)
- Oct. 2001 -> Late 2004 = 1 row per month. Last business day each month.
    - Jan 2003 missing
- ~April 2005 onward = Daily reporting

-  2025-08-04 shows a $10000000000.00 discrepancy
    - debt_held_public_amt + intragov_hold_amt) - tot_pub_debt_out_amt
- 2020 (COVID-era) showed largest jump in debt increase ($4.6 trillion). The macro trajectory matches known events 
    - Clinton-era surplus (1998-2000) $145B, $213B, $148B
    - Housing Crash (2008-2010) $1.5T, $1.7T, $1.8T
    - Trump-era tax cuts (2018. 2019) $1.3, 1.5T


- src_line_nbr column = Bronze-only metadata, not relevant for Silver layer