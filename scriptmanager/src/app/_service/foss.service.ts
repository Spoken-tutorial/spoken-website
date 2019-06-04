import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment} from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})



export class FossService {
 public env =  environment;
 public apiUrl = this.env['apiUrlScript']
  
  public getFoss(){
    return this.httpClient.get(`${this.apiUrl}/foss/`);
   
  }

  constructor(private httpClient: HttpClient) {}


}