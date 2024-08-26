# Hello!
Welcome to the Florest Library description page. The original is [here](https://pypi.org/project/florestdevinstruments/)
----------
# What am I?
I am the Florest library, written in Python and having extensive functionality that is only increasing every day.
I have 4 modules: `florest_utilits`, `working_document`, `ready_games` and `working_api`.
Each of these modules has its own purpose.
You can install the module using `pip install florestdevinstruments`. Download the latest version!
----------
# Examples of using
```python
from florestdevinstruments.florest_utilits import ai_image # import the "ai_image" function from the florest_utilits module.
with open('image.png', 'wb') as file: # create and open a .png file
    file.write(ai_image('Draw an old car.')) # write to our file as an image
    file.close() # save the image.
```

```python
from florestdevinstruments.ready_games import russian_rullet # import Russian roulette
answear = int(input(f'Enter your number from 1 to 3:'))
if russian_rullet(answear): # if the answer is correct, return True
    print(f'Congratulations!')
else:
    print(f'You lost!')
```

```python
from florestdevinstruments.working_api import VK # import the module "VK"
vk = VK('community app token', int('community ID')) # class initialization
print(f'Currently subscribed: {str(vk.get_subs())}) to the community.') # display the number of subscribers on the screen.
```
----------
# Author
Subscribe to my resources. [Click](https://telegra.ph/Socseti-Floresta-06-28)