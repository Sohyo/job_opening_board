import scrapy
import pandas as pd

class LeverSpider(scrapy.Spider):
    name = "lever"
    allowed_domains = ["jobs.lever.co"]

    # Load company data from CSV
    df = pd.read_csv("../job_name_list/eu_company_list.csv")
    start_urls = df[df["ATS_system"] == "Lever"]["career_page"].tolist()

    def parse(self, response):
        """Scrapes job openings from Lever career pages"""
        jobs = response.css("div.posting")

        for job in jobs:
            title = job.css("h5::text").get().strip()
            location = job.css("div.posting-categories span::text").get()
            job_url = response.urljoin(job.css("a::attr(href)").get())

            yield {
                "company": response.url.split("/")[-2],  # Extracts company name from URL
                "title": title,
                "location": location,
                "job_url": job_url
            }