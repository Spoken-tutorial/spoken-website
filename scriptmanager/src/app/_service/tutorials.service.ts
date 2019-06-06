import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment} from '../../environments/environment'



@Injectable({
  providedIn: 'root'
})



export class TutorialsService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']
  
  public getTutorials(fid){
    return this.httpClient.get(`${this.apiUrl}/${fid}`);
  }

  constructor(private httpClient: HttpClient) {} 


}