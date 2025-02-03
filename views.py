from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view # used for function based view
from rest_framework.decorators import APIView # used for class based view
from rest_framework.exceptions import ValidationError
import pymysql
from decimal import Decimal



# Create your views here.

def connection():
    db = pymysql.connect(
        host='localhost',
        user='root',
        password = 'root',
        database='car',
    )
    
    cur = db.cursor()
    return cur,db
cur,db = connection()

#---------------------------------------------------------
# by using Jsonresponse

# def car_list(request):

#     cur,db = connection()

#     query = cur.execute("select * from carlist")

#     data = cur.fetchall()
#     print(data)

#     car_data = []
#     # print(car_data) # will return [] becuase the exceutions of line by line

#     for row in data:
#         print(row)
#         car = {
#             "id":row[0],
#             "name":row[1],
#             "descriptions":row[2],
#             "active":row[3]
#         }
#         print(car)
#         result=car_data.append(car)
#         print(result)

#     cur.close()
#     db.close()

#     # By setting safe=False, you explicitly tell Django that it’s okay to serialize a non-dictionary object, such as a list.
#     return JsonResponse(car_data,safe=False)



# for the perticular data 

# def car_detail(request,pk):
#     cur,db=connection()
#     query=cur.execute("select * from carlist where id= %s",(pk,))
#     data = cur.fetchone()

#     if data:
#         list={
#             "id": data[0],
#             "name": data[1],
#             "descriptions": data[2],
#             "active": data[3]
#         }
 
#     cur.close()
#     db.close()
#     return JsonResponse(list,safe=False)

#--------------------------------------------------------------


# by using HttpResponse we can send the data in json format

# def car_list(request):

#     cur,db = connection()

#     query = cur.execute("select * from carlist")

#     data = cur.fetchall()
#     print(data)

#     car_data = []
#     # print(car_data) # will return [] becuase the exceutions of line by line

#     for row in data:
#         print(row)
#         car = {
#             "id":row[0],
#             "name":row[1],
#             "descriptions":row[2],
#             "active":row[3]
#         }
#         print(car)
#         result=car_data.append(car)
#         print(result)

#     cur.close()
#     db.close()

#     data_json = json.dumps(car_data)
#     return HttpResponse(data_json,content_type = 'application/json')


#------------------------------------------------------------------------

# creating API by using Functions based

# by deault this decorator get request

# Function to establish a database connection

def connection():
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='car',  # Ensure the database is correct
    )
    cur = db.cursor()
    return cur, db
    

# The car_list view handling both GET and POST requests
@api_view(['GET', 'POST'])
def car_list(request):
    if request.method == 'GET':
        cur, db = connection()
        
        query = cur.execute("SELECT * FROM carlist")
        data = cur.fetchall()  
        
        car_list_data = []
        discount_percentage = Decimal(10)  # Example: 10% discount

        for row in data:
            carlist = {
                "id": row[0],
                "name": row[1],
                "description": row[2],  
                "activate": row[3],
                "chessinumber":row[4],
                "price":row[5]

            }
            print(carlist)
            
            # Calculate the discounted price (10%)
            discounted_price = carlist['price'] - (carlist['price'] * (discount_percentage / Decimal(100)))
            print(discounted_price)
            carlist['discounted_price'] = discounted_price  # Add the discounted price to the dictionary
            car_list_data.append(carlist)
        
        cur.close()
        db.close()
        
        return JsonResponse(car_list_data, safe=False)

    elif request.method == 'POST':
        try:
   
            data = request.data
            name = data.get('name')
            description = data.get('description') 
            active = data.get('active', True) 
            chessinumber = data.get('chessinumber')
            price = data.get("price") 
            
            if not name or not description:
                return JsonResponse({"error": "Name and description are required."}, status=400)

            cur, db = connection()
            
            query = "INSERT INTO carlist (name, descriptions, active,chessinumber,price) VALUES (%s, %s, %s,%s,%s)"
            cur.execute(query, (name, description, active,chessinumber,price))
            db.commit() 
            

            cur.close()
            db.close()

            return JsonResponse({"message": "Car added successfully!"}, status=201)
        
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return JsonResponse({"error": "Database error, please try again later."}, status=500)
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)




@api_view(['GET','PUT','DELETE'])
def car_detail(request,pk):
    if request.method=='GET':
        try:
            cur,db = connection()
            query = cur.execute("select *from carlist where id=%s",(pk,))
            data = cur.fetchone()

            if data :
                cardetail={
                    "id":data[0],
                    "name":data[1],
                    "descriptions":data[2],
                    "activate":data[3],
                    "chessinumber":data[4],
                    "price":data[5]
                }
                cur.close()
                db.close()
                return JsonResponse(cardetail,safe=False)
            else:
                cur.close()
                db.close()
                return JsonResponse({"error": "Car not found."}, status=404)

        
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return JsonResponse({"error": "Database error, please try again later."}, status=500)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)




    
    elif request.method=='PUT':
        try:
            
            if not pk:
                return JsonResponse({"error": "Car ID is required to update."}, status=400)

            data = request.data
            name = data.get('name')
            descriptions = data.get('descriptions')
            active = data.get('active',True)
            chessinumber = data.get("chessinumber")
            price = data.get("price")
            

            # 1) field level validation :

            if price is not None:
                try:
                    price = float(price)  
                    if price < 50000:
                        return JsonResponse({"error": "Price must be greater than fifty thousand."}, status=400)
                except ValueError:
                    return JsonResponse({"error": "Invalid price value. It must be a number."}, status=400)
            else:
                price = None 

            # 2) object level validation :

            if not name or not descriptions:
                return JsonResponse({"error": "Name and description are required fields."}, status=400)

            
            if active and (price is None or price < 0):
                return JsonResponse({"error": "If the car is active, price must be provided and cannot be negative."}, status=400)

            if chessinumber and not isinstance(chessinumber, str):
                return JsonResponse({"error": "Chessinumber must be an string."}, status=400)
            
            # validator
            if active and price is None:
                raise ValidationError("Price is required if the car is active.")
    



            cur, db = connection()
            query="update carlist set name=%s , descriptions=%s, active=%s , chessinumber=%s, price=%s where id=%s "
            cur.execute(query,(name, descriptions, active, chessinumber, price, pk,))
            db.commit()

            cur.close()
            db.close()

            return JsonResponse({"message":"car updated successfully"})

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return JsonResponse({"error": "Database error, please try again later."}, status=500)

        except Exception as e:
            
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)



    elif request.method=="DELETE":
        try:
            if not pk:
                return JsonResponse({"message":"please provide the ID"})
            cur,db = connection()
            query="Delete from carlist where id=%s"
            cur.execute(query,(pk,))

            db.commit()
            cur.close()
            db.close()

            return JsonResponse({"message":"car is deleted successfully"})

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return JsonResponse({"error": "Database error, please try again later."}, status=500)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)







#----------------------------------------------------------------
# types of validations: there are three types of validations

# 1) field level validation :
# Validates individual fields (e.g., ensuring the name has at least 3 characters).

# 2) object level validation :Example:
# Validates the relationship between multiple fields or the entire object (e.g., ensuring price is provided if active is True).

# 3) validators :Reusable functions that validate specific conditions (can be applied to fields).



# 1) field level validation :

            # if price is not None:
            #     try:
            #         price = float(price)  
            #         if price < 50000:
            #             return JsonResponse({"error": "Price must be greater than fifty thousand."}, status=400)
            #     except ValueError:
            #         return JsonResponse({"error": "Invalid price value. It must be a number."}, status=400)
            # else:
            #     price = None 

# 2) object level validation :

            # if not name or not descriptions:
            #     return JsonResponse({"error": "Name and description are required fields."}, status=400)

            
            # if active and (price is None or price < 0):
            #     return JsonResponse({"error": "If the car is active, price must be provided and cannot be negative."}, status=400)

            # if chessinumber and not isinstance(chessinumber, str):
            #     return JsonResponse({"error": "Chessinumber must be an string."}, status=400)
            
# 3) validator
            # if active and price is None:
            #     raise ValidationError("Price is required if the car is active.")

#---------------------------------------------------------------------------------------------------


# Class Based View

class showroom(APIView):
    def get(self,request):
        con ,db = connection()
        query = cur.execute("SELECT * FROM showroom")
        data = cur.fetchall()

        showroom_list_data =[]

        for row in data:
            showroom_data={
                'id':row[0],
                'name':row[1],
                'location':row[2],
                'website':row[3]
            }

            showroom_list_data.append(showroom_data)
 
        
        return JsonResponse(showroom_list_data, safe=False)


    def post(self, request):
        try:
            data = json.loads(request.body)  
            

            name = data.get('name')
            location = data.get('location')
            website = data.get('website')

            if not name or not location or not website:
                return JsonResponse({"error": "Name, Location, and Website are required!"}, status=400)

            cur, db = connection()

            query = "INSERT INTO showroom (name, location, website) VALUES (%s, %s, %s)"
            
            cur.execute(query, (name, location, website))
            db.commit()

           
            return JsonResponse({"message": "Data Inserted Successfully!"})

        except pymysql.MySQLError as e:
            return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format!"}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if 'db' in locals() and db:
                db.close()



class showroom_list(APIView):
    def get(self,request,id):
        cur,db = connection()
        cur.execute("select * from showroom where id=%s",(id))
        data = cur.fetchone()

        if data is None:
            return JsonResponse({"error": "Showroom not found!"}, status=404)

        showroom_data =[]


        if data:
            showroom_list = {
                'id':data[0],
                'name':data[1],
                'location':data[2],
                'website':data[3],
            }

            showroom_data.append(showroom_list)
        cur.close()
        db.close()
        return JsonResponse(showroom_data,safe=False)

    
    def put(self, request, id):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            location = data.get('location')
            website = data.get('website')

            if not name or not location or not website:
                return JsonResponse({"error": "Name, Location, and Website are required!"}, status=400)

            cur, db = connection()

            
            cur.execute("SELECT * FROM showroom WHERE id = %s", (id,))
            if not cur.fetchone():
                return JsonResponse({"error": "Showroom not found!"}, status=404)

            query = "UPDATE showroom SET name = %s, location = %s, website = %s WHERE id = %s"
            cur.execute(query, (name, location, website, id))
            db.commit() 

          
            cur.close()
            db.close()

            return JsonResponse({"message": "Updated Successfully"})

        except pymysql.MySQLError as e:
            return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format!"}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)



    def delete(self,request,id):
        cur,db = connection()
        query = "delete from showroom where id=%s"
        cur.execute(query,(id))
        db.commit()
        cur.close()
        db.close()

        return JsonResponse({"message":"Succesfully Deleted"})

























         
















   












    












