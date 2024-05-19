from django.shortcuts import render
from store.models import Product,Advertisement
from category.models import Category

from django.http import JsonResponse
from pathlib import Path
import hashlib
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from store.models import ReviewRating


from langchain.text_splitter import RecursiveCharacterTextSplitter


from langchain_community.embeddings import GooglePalmEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory


from langchain.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate


from langchain_community.vectorstores import Qdrant
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from langchain.schema import SystemMessage
from langchain.chains import LLMChain












def index(request):

    # categories = Category.objects.all().filter(home_page_show=True)[:5]
    # first_category = categories[0]
    # second_category = categories[1]
    # third_category = categories[2]
    # fourth_category = categories[3]
    # fifth_category = categories[4]
    # sixth_category = categories[5]

    best_seller_products = Product.objects.all().filter(is_available=True,best_seller=True).order_by('-created_date')[:8]
    # offer_product = Product.objects.all().filter(is_available=True,offer_product=True).order_by('-created_date')[0]
    ads_new = Advertisement.objects.all().order_by('-created_date')
    ads_old = Advertisement.objects.all().order_by('created_date')

    context = {
        'products': best_seller_products,
        # 'first_category':first_category,
        # 'second_category':second_category,
        # 'third_category':third_category,
        # 'fourth_category':fourth_category,
        # 'fifth_category':fifth_category,
        # 'offer_product':offer_product,
        'ads_new':ads_new,
        'ads_old':ads_old,
    }

    return render(request,'index.html',context)






genai.configure(api_key=settings.GEMINI_API_KEY)

# Set up the model
generation_config = {
  "temperature": 0.5,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)





# uploaded_files = []
# def upload_if_needed(pathname: str) -> list[str]:
#   path = Path(pathname)
#   hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
#   try:
#     existing_file = genai.get_file(name=hash_id)
#     return [existing_file.uri]
#   except:
#     pass
#   uploaded_files.append(genai.upload_file(path=path, display_name=hash_id))
#   return [uploaded_files[-1].uri]

# def extract_pdf_pages(pathname: str) -> list[str]:
#   parts = [f"--- START OF PDF ${pathname} ---"]
#   # Add logic to read the PDF and return a list of pages here.
#   pages = []
#   for index, page in enumerate(pages):
#     parts.append(f"--- PAGE {index} ---")
#     parts.append(page)
#   return parts



def read_file_to_dict(file_path):
    data_dict = {
        "role": "user",
        "parts": []
    }
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            data_dict["parts"].append(file_content)
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return data_dict


file_path = 'adukkala_info.txt'
result = read_file_to_dict(file_path)





convo = model.start_chat(history=[
#   {
#     "role": "user",
#     "parts": extract_pdf_pages("<path>/document0.pdf")
#   },
result,
  # {
  #   "role": "user",
  #   "parts": ["hai"]
  # },
  # {
  #   "role": "model",
  #   "parts": ["Hello! I am Adukkala AI Chatbot. I am here to assist you with any questions you may have about Adukkala retail shop. Please feel free to ask me anything about our products, services, or store hours. I am here to help!"]
  # },
  # {
  #   "role": "user",
  #   "parts": ["where is the location of the shop?"]
  # },
  # {
  #   "role": "model",
  #   "parts": ["Adukkala retail shop is located at Jos Junction in Panampilly Nagar, Ernakulam district, Kerala state, India. Our exact address is:\n\n**Adukkala**\nJos Junction\nPanampilly Nagar\nErnakulam, Kerala 682036\nIndia\n\nWe are open every day of the week from 9:00 AM to 10:00 PM.\n\nIs there anything else I can assist you with today?"]
  # },
  # {
  #   "role": "user",
  #   "parts": ["what are the main products sold here?"]
  # },
  # {
  #   "role": "model",
  #   "parts": ["Adukkala retail shop sells a wide range of kitchen appliances and utensils, including:\n\n* Cookers\n* Plates\n* Gas stoves\n* Induction cookers\n* Flasks\n* Lunch boxes\n* Glasses\n* Dish sets\n* Ovens\n* Mixi\n* Grinders\n* Spoons\n\nWe carry a variety of brands, including Prestige, Butterfly, Preethi, Nolta, Hawkins, Milton, and Pigeon.\n\nWhether you are looking for basic kitchen essentials or high-end appliances, we have something to meet your needs. Our friendly and knowledgeable staff is always happy to help you find the perfect products for your kitchen.\n\nIs there anything else I can assist you with today?"]
  # },
  # {
  #   "role": "user",
  #   "parts": ["what all brands are available?"]
  # },
  # {
  #   "role": "model",
  #   "parts": ["Adukkala retail shop carries a wide range of kitchen appliance and utensil brands, including:\n\n* Prestige\n* Butterfly\n* Preethi\n* Nolta\n* Hawkins\n* Milton\n* Pigeon\n\nThese brands are known for their quality, durability, and innovation. We carefully select our products to ensure that we offer our customers the best possible selection of kitchenware.\n\nWhether you are looking for a new set of pots and pans, a new oven, or a new set of cutlery, we have something to meet your needs. Our friendly and knowledgeable staff is always happy to help you find the perfect products for your kitchen.\n\nIs there anything else I can assist you with today?"]
  # },
])



# for uploaded_file in uploaded_files:
#   genai.delete_file(name=uploaded_file.name)




@csrf_exempt
def chatbot_message_handler(request):
    
    name = None
    
    try:
    
      name = request.user.first_name
    except:
       pass  

    if request.method == 'POST':
        # Retrieve the user's message from the request
        user_message = request.POST.get('message')

        if name:
        
          convo.send_message(f'My name is {name},{user_message}')
        else:
          convo.send_message(user_message)

        # Retrieve the bot's reply from the conversation
        bot_reply = convo.last.text
        
        # Return the bot's reply as JSON response
        return JsonResponse({'reply': bot_reply})
    else:
        # Handle other HTTP methods (if needed)
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    






def about_us(request):
   return render(request,'store/about_us.html')









def chunk_data(data, chunk_size=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    chunks = text_splitter.split_documents(data)
    return chunks




def create_embeddings(chunks, api_key):

    embeddings = GooglePalmEmbeddings(google_api_key=api_key)

    try:
        shutil.rmtree("qrdrant_db")

    except:
        pass

   
    vector_store = Qdrant.from_documents(chunks, embeddings, path="qrdrant_db", collection="store")

    return vector_store




def ask_question(q,chain):
    result = chain.invoke({'question':q})
    return result



api_key = settings.GEMINI_API_KEY




def compare_ai(request,product1_id,product2_id):
    
    text = request.GET.get('text', '')
    
    product1 = Product.objects.get(id=product1_id)
    product2 = Product.objects.get(id=product2_id)

    reviews1 = ReviewRating.objects.filter(product_id=product1.id,status=True).order_by('-created_date')[:10]
    reviews2 = ReviewRating.objects.filter(product_id=product2.id,status=True).order_by('-created_date')[:10]
  
    product1_reviews = ''
    for review in reviews1:
        product1_reviews += f'{review.subject}:{review.review} '

    product2_reviews = ''
    for review in reviews2:
        product2_reviews += f'{review.subject}:{review.review} '  


    data1 = f'''Name of the product is {product1.product_name}.
    Is this product available in offer price:{product1.offer_product}.
    The features of this product are {product1.product_description}.
    The MRP price of this product is {product1.MRP_price} and the selling price is {product1.price}.
    is this product a best seller:{product1.best_seller}.
    The reviews of this product are {product1_reviews}.
    The average rating given to this product is {product1.averageReview()} out of {product1.countReview()} reviews.'''



    data2 = f'''Name of the product is {product2.product_name}.
    Is this product available in offer price:{product2.offer_product}.
    The features of this product are {product2.product_description}.
    The MRP price of this product is {product2.MRP_price} and the selling price is {product2.price}.
    is this product a best seller:{product2.best_seller}.
    The reviews of this product are {product2_reviews}.
    The average rating given to this product is {product2.averageReview()} out of {product2.countReview()} reviews.'''


    raw_data = f'''The details about {product1.product_name} are {data1}.
    The details about {product2.product_name} are {data2}.'''

    # file_name = "product_details.txt"
    # with open(file_name, "w") as file:
    #   file.write(raw_data)

    # loader = TextLoader(file_name)
    # final_data = loader.load()

    # chunks = chunk_data(final_data)
    # vector_store = create_embeddings(chunks,api_key)
    

    llm = ChatGoogleGenerativeAI(model='gemini-pro',temperature=0.7,google_api_key=api_key,convert_system_message_to_human=True)
    # retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 15})
    # memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True)



    # system_template = r'''
    #                 You are a product comparison expert of a kitchen utensils selling shop adukkala.
    #                 You help customers to choose the best product from the available options.
    #                 Use the following pieces of context to suggest the best product for the customer.

    #                 Context:```{context}```

    #                 ''' 

    # user_template = '''

    #               Question: ```{question}```
    #               Chat History: ```{chat_history}```
    #               '''
    # messages = [
    #             SystemMessagePromptTemplate.from_template(system_template),
    #             HumanMessagePromptTemplate.from_template(user_template)
    #             ]



    # qa_prompt = ChatPromptTemplate.from_messages(messages)

                        

    # crc = ConversationalRetrievalChain.from_llm(
    #                             llm = llm,
    #                             retriever = retriever,
    #                             chain_type='stuff',
    #                             memory=memory,
    #                             combine_docs_chain_kwargs={'prompt':qa_prompt},
    #                             verbose=True
    #                         )
                            


                            
    # q = 'Please suggest the name of the best product for me from these two products, also explain why you found this product to be the best option,i want a affordable quality item '
    # q = 'please prepare a summary on this data'

    # suggestion = ask_question(q,crc)
                            
    prompt = ChatPromptTemplate(
    input_variables=["content"],
    messages=[
        SystemMessage(content="You are a product comparison expert of a kitchen utensils selling shop adukkala.You help customers to choose the best product from the available options.Use the following information given by the customer and suggest the name of the best product for the customer.Also explain why you found this product to be the best option in points"),
        # SystemMessage(content='You respond only in German.'),
        HumanMessagePromptTemplate.from_template("{content}")
    ]
    )



    chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True
    )

    response = chain.invoke({'content': f'{raw_data} Please suggest the name of the best product for me from these two products, also consider {text}'})


    context = {
       'product1':product1,
       'product2':product2,
       'suggestion':response["text"],
       
    }

    return render(request,'store/compare_ai.html',context)