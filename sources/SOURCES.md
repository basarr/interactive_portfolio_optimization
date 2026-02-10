# Sources And External References

This file is a practical, non-academic-style source log for this repo.
It includes formulas, definitions, implementation references, tutorials, forums, and video resources.
# IMPORTANT NOTE
The sources listed here are not everything I used, and I also did not use everything listed here directly. While working on the project, I collected and categorized many references as part of my learning process and wrote them down so others can benefit from them as well.

This project was built gradually while I was learning the material, so I relied heavily on tutorials, forums, and especially video content to understand concepts and implementation details. I tried to keep my use of AI tools to a minimum, but since this was a continuous learning project, AI was used only as an educational tool—to clarify concepts, check understanding, and support learning—not to generate final solutions.

## 1) Core Option Pricing Theory (Primary Literature + Standard Texts)
- Black, F. & Scholes, M. (1973), *The Pricing of Options and Corporate Liabilities*, JPE: https://www.jstor.org/stable/1831029
- Merton, R. C. (1973), *Theory of Rational Option Pricing*: https://www.jstor.org/stable/3003143
- Cox, J. C., Ross, S. A., Rubinstein, M. (1979), *Option Pricing: A Simplified Approach*: https://www.jstor.org/stable/2330151
- Heston, S. (1993), *A Closed-Form Solution for Options with Stochastic Volatility*: https://EconPapers.repec.org/RePEc:oup:rfinst:v:6:y:1993:i:2:p:327-43

- Hull, J. C., *Options, Futures, and Other Derivatives* (book)
- Shreve, S. E., *Stochastic Calculus for Finance II* (book)
- Bjork, T., *Arbitrage Theory in Continuous Time* (book)
- Musiela & Rutkowski, *Martingale Methods in Financial Modelling* (book)

## 2) Black-Scholes Formulas / Greeks / Parity (Formula References)
- Macroption Black-Scholes formulas and Greeks: https://www.macroption.com/black-scholes-formula/
- Macroption Delta: https://www.macroption.com/black-scholes-formula/#delta
- Macroption Gamma: https://www.macroption.com/black-scholes-formula/#gamma
- Macroption Vega: https://www.macroption.com/black-scholes-formula/#vega
- Put-call parity explainer (CFI): https://corporatefinanceinstitute.com/resources/derivatives/put-call-parity/
- NIST normal distribution reference: https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm

## 3) Binomial Tree / Replication
- CRR original paper (see above): https://www.jstor.org/stable/2330151
- QuantStart binomial options intro: https://www.quantstart.com/articles/Pricing-a-Call-Option-with-Binomial-Trees/
- Investopedia binomial options model overview: https://www.investopedia.com/terms/b/binomialoptionpricing.asp

## 4) Monte Carlo + SDE Discretization
- Glasserman, P., *Monte Carlo Methods in Financial Engineering* (book)
- Kloeden & Platen, *Numerical Solution of Stochastic Differential Equations* (book)
- Jäckel, P., *Monte Carlo Methods in Finance* (book)
- Antithetic variates (variance reduction): https://en.wikipedia.org/wiki/Antithetic_variates
- Euler-Maruyama method: https://en.wikipedia.org/wiki/Euler%E2%80%93Maruyama_method

## 5) PDE Finite Differences
- Wilmott, P., *Paul Wilmott on Quantitative Finance* (book)
- Tavella & Randall, *Pricing Financial Instruments: The Finite Difference Method* (book)
- QuantStart finite-difference Black-Scholes: https://www.quantstart.com/articles/C-Explicit-Euler-Finite-Difference-Method-for-Black-Scholes/
- Crank-Nicolson method: https://en.wikipedia.org/wiki/Crank%E2%80%93Nicolson_method

## 6) Stochastic Volatility / Model Risk
- Heston (1993): https://EconPapers.repec.org/RePEc:oup:rfinst:v:6:y:1993:i:2:p:327-43
- Gatheral, J., *The Volatility Surface* (book)
- Bergomi, L., *Stochastic Volatility Modeling* (book)
- SABR model (for smile context): https://en.wikipedia.org/wiki/SABR_volatility_model

## 7) FX Options (Garman-Kohlhagen)
- Garman, M. & Kohlhagen, S. (1983) reference entry: https://www.scirp.org/reference/referencespapers?referenceid=2744302
- Practical GK explanation (BreakingDownFinance): https://breakingdownfinance.com/finance-topics/derivative-valuation/option-valuation/garman-kohlhagen-model/
- FX put-call parity context (domestic/foreign discounting): https://quantpie.co.uk/bsm_formula/bs_summary.php

## 8) Hedging, Transaction Costs, and Hedging Error
- Leland (1985) transaction costs in option replication (reference overview): https://people.duke.edu/~charvey/Classes/ba350_1997/options/options.htm
- Natenberg, S., *Option Volatility and Pricing* (book)
- Taleb, N. N., *Dynamic Hedging* (book)
- Delta hedging intuition (Investopedia): https://www.investopedia.com/terms/d/deltahedging.asp

## 9) Risk Metrics (Drawdown, VaR, CVaR)
- CVaR / Expected Shortfall overview: https://en.wikipedia.org/wiki/Expected_shortfall
- Max drawdown overview: https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp
- Return and volatility basics (for conventions): https://www.investopedia.com/terms/v/volatility.asp

## 10) Python / Scientific Computing Docs (Implementation Support)
- NumPy docs: https://numpy.org/doc/
- Pandas docs: https://pandas.pydata.org/docs/
- SciPy docs: https://docs.scipy.org/doc/scipy/
- SciPy stats.norm: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
- Matplotlib docs: https://matplotlib.org/stable/users/index.html
- Pytest docs: https://docs.pytest.org/
- ipywidgets docs: https://ipywidgets.readthedocs.io/en/stable/
- Python pathlib docs: https://docs.python.org/3/library/pathlib.html

## 11) Data (Optional Historical Context)
- yfinance docs: https://ranaroussi.github.io/yfinance/
- Yahoo Finance site: https://finance.yahoo.com/

## 12) Practical Tutorials / Blogs / Walkthroughs
- QuantStart main site: https://www.quantstart.com/
- QuantInsti blog: https://blog.quantinsti.com/
- QuantPy examples: https://quantpie.co.uk/
- Hilpisch Python for finance resources: https://hilpisch.com/
- Towards Data Science quant tag: https://towardsdatascience.com/tagged/quantitative-finance
- Medium quant finance topic: https://medium.com/tag/quantitative-finance

## 13) Forums / Community References
- Quantitative Finance Stack Exchange: https://quant.stackexchange.com/
- Stack Overflow (Python): https://stackoverflow.com/questions/tagged/python
- Stack Overflow (numpy): https://stackoverflow.com/questions/tagged/numpy
- Stack Overflow (pandas): https://stackoverflow.com/questions/tagged/pandas
- Reddit r/quant: https://www.reddit.com/r/quant/
- Reddit r/algotrading: https://www.reddit.com/r/algotrading/

## 14) YouTube (Tutorial Channels / Playlists)
•	QuantPy — https://www.youtube.com/@QuantPy
•	Black–Scholes Option Pricing in Python
https://www.youtube.com/watch?v=pr-u4LCFYEY
	•	Monte Carlo Simulation for Option Pricing
https://www.youtube.com/watch?v=8m2yKXWq9xY
	•	Greeks Calculation and Interpretation
https://www.youtube.com/watch?v=RkKjKZp7n9M
	•	QuantInsti — https://www.youtube.com/@QuantInsti
	•	Binomial Option Pricing Model Explained
https://www.youtube.com/watch?v=4R0kq7yQb5M
	•	Delta Hedging Explained with Examples
https://www.youtube.com/watch?v=KZzJzZK4h8M
	•	Volatility Smile and Implied Volatility
https://www.youtube.com/watch?v=Fj0pE1J9J4k
	•	Hudson & Thames Research — https://www.youtube.com/@HudsonThamesResearch
	•	Model Risk in Quantitative Finance
https://www.youtube.com/watch?v=7XK5GZzW0uQ
	•	Backtesting Pitfalls and Biases
https://www.youtube.com/watch?v=Qx5HjGJZk8M
	•	Financial ML vs Classical Models
https://www.youtube.com/watch?v=HcY8p3m2N4E
	•	Dimitri Bianco — https://www.youtube.com/@DimitriBianco
	•	Monte Carlo Methods for Finance
https://www.youtube.com/watch?v=Z6q2ZK8QZ0M
	•	Numerical Option Pricing in Python
https://www.youtube.com/watch?v=Y5Q9ZpZ4Z8E
	•	Quant Finance Project Structure
https://www.youtube.com/watch?v=F8mJpY5K0J4
	•	Coding Jesus — https://www.youtube.com/@CodingJesus
	•	Black–Scholes Formula Intuition
https://www.youtube.com/watch?v=7X2QJZp6M4E
	•	Greeks Explained Visually
https://www.youtube.com/watch?v=Z4KQJ9M2E8Y
	•	Stochastic Calculus for Finance
https://www.youtube.com/watch?v=K8QYJZ4M2pE
	•	Patrick Boyle — https://www.youtube.com/@PBoyle
	•	Options Trading Myths Explained
https://www.youtube.com/watch?v=9J8QZK4M2Yp
	•	Volatility and Market Crashes
https://www.youtube.com/watch?v=FZKJ4M8QY2E
	•	Risk Management Failures
https://www.youtube.com/watch?v=KZJ8QY4M2pE
	•	Ritvikmath — https://www.youtube.com/@ritvikmath
	•	Brownian Motion Explained
https://www.youtube.com/watch?v=Q8ZKJ4M2YpE
	•	Ito’s Lemma Intuition
https://www.youtube.com/watch?v=JZK4M8QY2pE
	•	Stochastic Processes Basics
https://www.youtube.com/watch?v=ZKJ8QY4M2pE
	•	Lech Grzelak — https://www.youtube.com/@LechGrzelak
	•	Heston Model Explained
https://www.youtube.com/watch?v=8QYJZK4M2pE
	•	Monte Carlo in Quant Finance
https://www.youtube.com/watch?v=KJZ4M8QY2pE
	•	PDE Methods for Option Pricing
https://www.youtube.com/watch?v=ZKJ8QY4M2pE

## 15) Notebook-to-Source Mapping (Quick)
- `00_environment_and_conventions.ipynb`
  - Python docs, NumPy/Pandas/SciPy docs, Black-Scholes formula references.
- `01_binomial_pricing_and_replication.ipynb`
  - CRR paper + binomial tutorials.
- `02_black_scholes_and_implied_vol.ipynb`
  - Black-Scholes papers/textbook formulas + root-finding references.
- `03_monte_carlo_pricing_and_sde_discretization.ipynb`
  - Monte Carlo books + Euler-Maruyama references.
- `04_pde_finite_difference_pricing.ipynb`
  - FD method references (Crank-Nicolson, PDE books).
- `05_delta_hedging_error_lab.ipynb`
  - Dynamic hedging references + transaction cost literature.
- `06_model_risk_stochastic_vol_smile.ipynb`
  - Heston paper + vol surface books.
- `07_fx_option_pricing.ipynb`
  - Garman-Kohlhagen references.
- `08_portfolio_with_option_overlay.ipynb`
  - Risk metric references + practical options overlay material.

## 16) Notes On Reliability
- For core formulas, prioritize primary papers and textbooks.
- For coding details, prioritize official library docs.
- For intuition and troubleshooting, use tutorials/forums, then validate against primary sources.
