# Google Reviews Scraper
the scrape_reviews function extracts the google reviews from a given url like the following:
https://www.google.com/search?sxsrf=ALeKk01F-VC1fLWomiH1vKevVrnActfWwg%3A1601038658827&ei=QultX9DsMY-asAeeiY7QBA&q=MCDONALD%27S%2C+New+York+City+-+490+8th+Ave&oq=MCDONALD%27S%2C+New+York+City+-+490+8th+Ave&gs_lcp=CgZwc3ktYWIQAzoECAAQR1CbdFjwjAFgqZEBaABwBHgAgAFUiAFUkgEBMZgBAaABAqABAaoBB2d3cy13aXrIAQjAAQE&sclient=psy-ab&ved=0ahUKEwjQlZ_krYTsAhUPDewKHZ6EA0oQ4dUDCAw&uact=5#lrd=0x89c25996bae1317f:0xc9f293d62d45b907,1,,,

After searching for the location and insuring a side panel for google maps on the right is shown. Click the blue "#number Google reviews" and a window will pop up, That's when you copy the link for the scraper.
The pop up window is used to extract the reviews.

The script also logs in to a google account so make sure to set the username and password inside the google_login function.
This script is designed to be used continuously on a loop because it avoids recaptcha and blockage as much as possible.
