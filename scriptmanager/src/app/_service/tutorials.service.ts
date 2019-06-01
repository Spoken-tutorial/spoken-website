import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Foss } from '../_class/foss';


@Injectable({
  providedIn: 'root'
})



export class TutorialsService {
  // apiURL: string = 'http://localhost:8000/scripts/api';
  
  public getTutorials(){
    console.log("manan")
    // return this.httpClient.get<Foss[]>(`${this.apiURL}/foss/`);
    var tutorials = [
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
    return tutorials;

  }

  constructor(private httpClient: HttpClient) {
    // console.log(this.getCustomerById())

  }


}