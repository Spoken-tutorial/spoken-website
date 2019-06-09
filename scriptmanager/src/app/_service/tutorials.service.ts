import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment} from '../../environments/environment'



@Injectable({
  providedIn: 'root'
})



export class TutorialsService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']
  
  /*
  * Fetches the tutorials for all foss categories
  * user is part of
  */
  public getAllTutorials() {
    return this.getFossTutorials('all');
  }
  
  /*
  * Fetches tutorails for foss category of 
  * provdied fid
  */
  public getFossTutorials(fid){
    const _url = `${this.apiUrl}/foss/${fid}/tutorials/`
    return this.httpClient.get(_url);
  }

  constructor(private httpClient: HttpClient) {} 


}