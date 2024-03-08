from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
from models.site import SiteModel
from sql_alchemy import banco
import sqlite3
import json


# path /hoteis?cidade=Rio de Janeiro&estrelas_min=4&estrelas_max=5&diaria_min=200&diaria_max=400
 
class Hoteis(Resource):
    query_params = reqparse.RequestParser()
    query_params.add_argument("cidade", type=str, default="", location="args")
    query_params.add_argument("estrelas_min", type=float, default=0, location="args")
    query_params.add_argument("estrelas_max", type=float, default=0, location="args")
    query_params.add_argument("diaria_min", type=float, default=0, location="args")
    query_params.add_argument("diaria_max", type=float, default=0, location="args")
 
    def get(self):
        filters = Hoteis.query_params.parse_args()
 
        query = HotelModel.query
 
        if filters["cidade"]:
            query = query.filter(HotelModel.cidade == filters["cidade"])
        if filters["estrelas_min"]:
            query = query.filter(HotelModel.estrelas >= filters["estrelas_min"])
        if filters["estrelas_max"]:
            query = query.filter(HotelModel.estrelas <= filters["estrelas_max"])
        if filters["diaria_min"]:
            query = query.filter(HotelModel.diaria >= filters["diaria_min"])
        if filters["diaria_max"]:
            query = query.filter(HotelModel.diaria <= filters["diaria_max"])
 
        return {"hoteis": [hotel.json() for hotel in query]}

class Hotel(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank") 
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank")
    argumentos.add_argument('diaria', type=float, required=True, help="The field 'diaria' cannot be left blank")
    argumentos.add_argument('cidade', type=str, required=True, help="The field 'cidade' cannot be left blank")
    argumentos.add_argument('site_id', type=int, required=True, help="Every hotel needs to be linked with a site.")

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message' : 'Hotel not found.'}, 404

    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {'message' : 'Hotel already exists.'}, 400

        print("Entrei na função")
        dados = Hotel.argumentos.parse_args() 
        print(dados)
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados['site_id']):
            return {'message': 'The hotel must be associated to a valid site id.'}, 400
        #try:
        hotel.save_hotel()
        #except:
          #  return {'message' : 'An internal error ocurred trying to save hotel.'}, 500
        return hotel.json(), 200
    
    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()

        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)

            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except Exception as e:
            return {'message': f'An error ocurred trying to create hotel. {e}'}, 500
        
        return hotel.json(), 201

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An error ocurred trying to delete hotel.'}, 500
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found.'}, 404

