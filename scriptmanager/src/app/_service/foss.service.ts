import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Foss } from '../_class/foss';


@Injectable({
  providedIn: 'root'
})



export class FossService {
  apiURL: string = 'http://localhost:8000/scripts/api';
  
  public getFoss(){
    return this.httpClient.get<Foss[]>(`${this.apiURL}/foss/`);
    // var Foss = [
    //   {
    //   "foss_category": 61,
    //   "language": 2,
    //   "user": 1055,
    //   "status": true
    //   },
    //   {
    //     "foss_category": 50,
    //     "language": 1,
    //     "user": 1055,
    //     "status": true
    //   }
    // ]
    // return Foss;

  }

  constructor(private httpClient: HttpClient) {
    // console.log(this.getCustomerById())

  }


}