steps
- postgres advanced (full text search)
- files
- tests
- deployment dev / prod
- debugging
- CICD
- ruff
- toml
- logs

https://www.youtube.com/watch?v=tiBeLLv5GJo
https://stackoverflow.com/questions/69670125/how-to-log-raw-http-request-response-in-fastapi
https://www.youtube.com/watch?v=cjkJVBX6jU8
https://www.nashruddinamin.com/blog/running-scheduled-jobs-in-fastapi
https://fastapi.tiangolo.com/advanced/events/#async-context-manager

https://stackoverflow.com/questions/77001129/how-to-configure-fastapi-logging-so-that-it-works-both-with-uvicorn-locally-and

- async
- logging
- caching
- streaming
- configs
- testing
- deployment
- docker
- debugging
- CICD




DB TABLES
    - MONGO
        - ITEMS
            - parmeters
            - description
            - links to images
    - POSTGRE
        - USERS
            - ADDRESSES
        - TRANSACTIONS
        



Item
    Category [clothes, shoes, Other]
    Subcategory: str
    Type: str
    Size: str
    Condition: str
    Material: str
    Color: str
    Pattern: str
    Brand: str
    Price: str
    
T-shirts
    Fit [Skinny, Slim, Regular, Relaxed, Oversized]
    Sleeves [Sleeveless, Short, Elbow, 3/4, Long]
    Collar [Backless, Button down, Cowl neck, Envelope, Henley, Hood, Polo, Square, V, Zip]

Trousers
    Length [Normal, Short, Knee-length, Calf-length, 3/4, 7/8, Ankle, Long]
    Fit [Skinny, Slim, Regular, Relaxed]
    Shape [Straight, Fitted, Flared, Tapered, Cocoon]
    Rise [Low, Normal, High]

shoes
    Fastener [Buckle, Laces, Hook-and-loop, Slip-on, Straps, Zip]
    Toe [Open, Rointed, Round, Square Toe]
    Width [Narrow, Regular, Large]




Tops
    T-shirts
    Blouses
    Sweaters
    Hoodies

Bottoms
    Jeans
    Trousers
    Shorts
    Skirts
    
Dresses
    Casual Dresses
    Formal Dresses
    Maxi Dresses
    Mini Dresses

Outerwear
    Jackets
    Coats
    Blazers
    Vests

Footwear
    Sneakers
    Boots
    Sandals
    Heels

Accessories
    Bags
    Belts
    Scarves
    Hats

Activewear
    Sports Bras
    Leggings
    Gym Shorts
    Tracksuits

Underwear & Loungewear
    Bras
    Panties
    Pajamas
    Robes