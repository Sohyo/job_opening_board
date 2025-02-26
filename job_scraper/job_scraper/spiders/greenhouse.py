import scrapy
import pandas as pd


class GreenhouseSpider(scrapy.Spider):

    name = "greenhouse"
    allowed_domains = ["boards.greenhouse.io", "job-boards.greenhouse.io"]
    custom_settings = {
        "REDIRECT_ENABLED": True,  # Allow redirects
        "COOKIES_ENABLED": False,  # Disable cookies to prevent tracking
        "ROBOTSTXT_OBEY": False,  # Ignore robots.txt restrictions
        "DOWNLOAD_DELAY": 1,  # Add delay to avoid being blocked
    }

    def start_requests(self):
        """Dynamically load URLs from the CSV and request them"""
        try:
            df = pd.read_csv("../job_name_list/eu_company_list.csv")  # Ensure this file exists
            greenhouse_urls = df[df["ATS_system"] == "Greenhouse"]["career_page"].tolist()
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            return

        for url in greenhouse_urls:
            fixed_url = url.replace("boards.greenhouse.io", "job-boards.greenhouse.io")
            yield scrapy.Request(url=fixed_url, callback=self.parse, meta={"original_url": url})

    def parse(self, response):
        """Scrapes job postings from Greenhouse, checking multiple structures"""

        jobs = response.css("div.opening")  # Standard Greenhouse job listings
        if not jobs:
            jobs = response.css("div.job-posts")  # Alternative structure
        if not jobs:
            jobs = response.css("div.level-0")  # Another possible structure

        # Log a warning if no jobs are found
        if not jobs:
            self.logger.warning(f"No job listings found on {response.url} - Check manually!")

        for job in jobs:
            title = job.css("a::text").get(default="").strip()
            location = job.css("span.location::text, div.location::text").get(default="").strip()
            job_url = response.urljoin(job.css("a::attr(href)").get(default=""))

            yield {
                "company": response.meta["original_url"].split("/")[-1],
                "title": title,
                "location": location,
                "job_url": job_url
            }