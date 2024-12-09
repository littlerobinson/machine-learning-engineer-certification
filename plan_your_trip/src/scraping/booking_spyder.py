import logging
import scrapy

logger = logging.getLogger(__name__)

# need to install scrapy-user-agents : pip install scrapy-user-agents

class BookingSpider(scrapy.Spider):

    name = 'booking_spider'

    start_urls = ['https://www.booking.com/index.fr.html']

    cities = []

    def __init__(self, cities = [], *args, **kwargs):
        logger.info('Init BookingSpider')
        self.cities = cities

    # Callback function that will be called when starting your spider
    def parse(self, response):
        logger.info('BookingSpider start to parse')
        # Use form request to search in booking for each cities
        try:
            for city in self.cities:
                logger.debug(f'Loop on city {city['name']}')
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={'ss': city['name']},
                    # Callback, call method to get hotels for one city
                    callback=self.search_for_city,
                    meta={'city_name': city['name'], 'city_id': city['id']}
                )
            
            logger.info('BookingSpider finish to parse')
        except KeyError:
            logger.error('error to scrap data in search page')
        except Exception as e:
            logger.error(e)


    # Search in page with the list of hotels in a city
    def search_for_city(self, response):
        try:
            hotel_cards = response.xpath('//div[@data-testid="property-card-container"]')
            for property_card in hotel_cards:
                url = property_card.xpath('.//a[@data-testid="title-link"]').attrib['href']
                name = property_card.xpath('.//a[@data-testid="title-link"]/div/text()').get()
                score = property_card.xpath('.//div[@data-testid="review-score"]/div/text()').get()
                description = property_card.xpath('.//div[@class="b290e5dfa6"]/text()').get()

                # Merge response meta with the new one 
                meta = response.meta | {'name': name, 'score': score, 'description': description}

                yield scrapy.Request(
                    url = response.urljoin(url),
                    callback = self.search_for_hotel,
                    meta = meta
                )
        except KeyError:
            logger.error('error to scrap data in city hotels')
        except Exception as e:
            logger.error(e)

    # Search in a hotel page
    def search_for_hotel(self, response):
        try:
            city = response.meta['city_name']
            city_id = response.meta['city_id']
            name = response.meta['name']
            score = response.meta['score']
            description = response.meta['description']

            gps_coordinates = response.xpath('//a[@id="hotel_address"]/@data-atlas-latlng').get()
            full_description = response.xpath('//p[@data-testid="property-description"]/text()').get()

            # Log the additional information or process it as needed
            logger.debug(f"GPS coordinates info for hotel {name}: {gps_coordinates}")

            yield {
                'url': response.request.url,
                'search_city': city,
                'city_id': city_id,
                'search_id': city_id,
                'name': name,
                'score': score,
                'description': description,
                'full_description': full_description,
                'gps_coordinates': gps_coordinates,
            }
        except KeyError:
            logger.error('error to scrap data for hotel')
        except Exception as e:
            logger.error(e)