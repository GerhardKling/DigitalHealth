********************************************************************************
* ASEAN DATA ANALYSIS
********************************************************************************
*Version 1
*GK

*Version 2
**Merge data from WDI

*Version 3
**Refactor code

*==============================================================================*

*==============================================================================*
*WDI data wrangling
*==============================================================================*
cd "C:\Users\User\Documents\Gerhard\Aberdeen HOME\PROJECTS\ASEAN\Data\World Bank"
insheet using "WDI health expenditure.csv", clear

*Country identifier
rename v1 iso

*Duplicate observations
expand 20

*Sort data by iso and count observations
sort iso
by iso: gen year=_n+1999

*Create variable
gen h_exp=.

forvalues i=2/21 {
	replace h_exp=v`i' if year==1998+`i'
	}
	
*Remove variables
drop v*

*Sort and save
sort iso year

cd "C:\Users\User\Documents\Gerhard\Aberdeen HOME\PROJECTS\ASEAN\Stata"
save WDI.dta, replace

*==============================================================================*
*Merge WDI data
*==============================================================================*
cd "C:\Users\User\Documents\Gerhard\Aberdeen HOME\PROJECTS\ASEAN\Stata"
use ASEAN.dta, clear

sort iso year
merge iso year using WDI.dta
drop _merge

save ASEAN_FINAL.dta, replace

*==============================================================================*
*Labels
*==============================================================================*
use ASEAN_FINAL.dta, clear

*Core variables in The Conference Board Total Economy Database
*Output, Labor and Labor Productivity, 1950-2021: CBTED1 and CBTED2
label var r_gdp	"Real GDP, in billions of 2020 international dollars, converted using Purchasing Power Parities, CBTED1"
label var n_gdp	"Nominal GDP, in billions of current international dollars, converted using Purchasing Power Parities, CBTED1"
label var emp "Persons employed (millions), CBTED1"
label var hours "Average annual hours worked per worker, CBTED1"
label var t_hours "Total annual hours worked (millions), CBTED1"
label var pop "Midyear population (millions), CBTED1"
label var out_p "Labour productivity per person employed in 2020 international dollars, converted using Purchasing Power Parities, CBTED1"
label var out_h "Labour productivity per hour worked in 2020 international dollars, converted using Purchasing Power Parities, CBTED1"
label var inc_pc "GDP per capita in 2020 international dollars, converted using Purchasing Power Parities, CBTED1"
label var gdp_g "Growth of GDP, per cent change, CBTED1"
label var emp_g "Growth of employment, per cent change, CBTED1"
label var t_hours_g "Growth of total hours worked, per cent change, CBTED1"
label var pop_g "Growth of population, per cent change, CBTED1"
label var out_p_g "Growth of Labor Productivity per person employed, per cent change, CBTED1"
label var out_h_g "Growth of Labor Productivity per hour worked, per cent change, CBTED1"
label var inc_pc_g "Growth of GDP per capita, per cent change, CBTED1"
label var gdp "GDP, CBTED2"
label var l_quant "Labor Input - Quantity, CBTED2"
label var l_qual "Labor Input - Quality, CBTED2"
label var c_total "Capital Input - Total, CBTED2"
label var c_ict "Capital Input - ICT, CBTED2"
label var c_non_ict "Capital Input - Non ICT, CBTED2"
label var l_quant_c "Labor Quantity Contribution, CBTED2"
label var l_qual_c "Labor Quality Contribution, CBTED2"
label var c_total_c "Total Capital Contribution, CBTED2"
label var c_ict_c "ICT Capital Contribution, CBTED2"
label var c_non_ict_c "Non-ICT Capital Contribution, CBTED2"
label var tfp "Total Factor Productivity, CBTED2"
label var l_share "Labor Share, CBTED2"
label var c_share "Capital Share, CBTED2"
label var ict_share "ICT Capital Share, CBTED2"
label var non_ict_share "Non-ICT Capital Share, CBTED2"

*Additional labels
label var index "Index from Pandas DataFrame"
label var region "Region"
label var country "Name of country"
label var iso "Country identifier"
label var year "Year"
label var l_quant_g "Labor Input - Quantity, log growth"
label var c_ict_g "Capital Input - ICT, log growth"
label var c_non_ict_g "Capital Input - Non ICT, log growth"

*WDI labels
label var h_exp "Current health expenditure per capita, current USD"


*==============================================================================*
*Growth decomposition
*==============================================================================*
encode iso, generate(code) 
label var code "Country identifier, numeric"

*Define panel
tsset code year

*Change order
drop index
order code year iso region country 

*Log returns
gen y = ln(r_gdp/pop) - ln(l.r_gdp/l.pop)
label var y "Growth in real GDP per capita, log returns"

gen c = ln(c_ict/pop) - ln(l.c_ict/l.pop)
label var c "Growth in ICT capital input per capita, log returns"

gen k = ln(c_non_ict/pop) - ln(l.c_non_ict/l.pop)
label var k "Growth in non-ICT capital input per capita, log returns"

gen l = ln(emp/pop) - ln(l.emp/l.pop)
label var l "Growth in share of employed population, log returns"

*Panel regressions
*Define constraint
constraint 1 l = 1-k-c

*Interaction term
gen ASEANxc = ASEAN * c
gen ASEANxk = ASEAN * k
gen ASEANxl = ASEAN * l

qui: {
	reg y c k l
	estimates store A

	xtreg y c k l, fe
	estimates store B

	cnsreg y c k l, constraint(1)
	estimates store C
	
	xi: reg y c k l ASEANxc ASEANxk ASEANxl ASEAN i.year 
	estimates store D
	}


estimates table A B C D, star b(%9.3f) keep(c k l ASEAN ASEANxc ASEANxk ASEANxl) stats(N, ll, F)


*==========>>>>> TABLE: growth regressions <<<<<<<<<<<<<========================
*Change directory for figures & tables
cd "C:\Users\User\Documents\Gerhard\Aberdeen HOME\PROJECTS\ASEAN\Tables"
estout A B C D using growth_regressions.xls, cells(b(star fmt(3)) p(par fmt(3))) ///
replace stats(N ll aic bic) keep(c k l ASEAN ASEANxc ASEANxk ASEANxl)
cd "C:\Users\User\Documents\Gerhard\Aberdeen HOME\PROJECTS\ASEAN\Stata"
*==========>>>>> TABLE: growth regressions <<<<<<<<<<<<<========================



*==============================================================================*
*Panel VAR: Reduced form
*==============================================================================*
*Fixed-effects do not matter
global var "y c k l h_growth"
foreach y of global var {
	qui: xtreg `y' l.y l.c l.k l.l l.h_growth, fe 
	matrix b = get(_b)
	matrix m_`y' = b'
	*Granger causality tests
	test l.y l.c l.k l.l l.h_growth
	foreach y of global var {
		test l.`y'
		}
	}

matrix C = (m_y, m_c, m_k, m_l, m_h_growth)
*Remove constant term
matrix C = C[1..5, 1..5]














