# leetcode-problem-parser
A crawler that scrapes problem information from Leetcode, a popular interview preparation site.

### Dependencies:
- Python3 and pip dependencies listed in `requirements.txt`
- chromedriver executable for your operating system. [Here](https://chromedriver.chromium.org/downloads) is the downloads page. This must be at the root level of where you call the script from
- `leetcode.html` file as the single source of truth for links to Leetcode problems right now. We want to keep this static because we want to have some control over the changes that happen.
