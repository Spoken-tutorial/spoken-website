import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Foss } from './foss';


@Injectable({
  providedIn: 'root'
})



export class ApiService {
  apiURL: string = 'https://cors-anywhere.herokuapp.com/http://localhost:8000/scripts/api';
  
  public getFoss(){
    console.log("manan")
    // return this.httpClient.get<Foss[]>(`${this.apiURL}/foss/`);
    var Foss = [
      {
      "foss_category": 61,
      "language": 2,
      "user": 1055,
      "status": true
      },
      {
        "foss_category": 50,
        "language": 1,
        "user": 1055,
        "status": true
      }
    ]
    return Foss;

  }

  constructor(private httpClient: HttpClient) {
    // console.log(this.getCustomerById())

  }


}