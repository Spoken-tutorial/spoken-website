import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment} from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})

export class TutorialsService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']
  
  // API service for fetching a list of all tutorials for the selected foss Id and language ID
  public getFossTutorials(fossId, languageId){
    const _url = `${this.apiUrl}/foss/${fossId}/language/${languageId}/tutorials/`
    return this.httpClient.get(_url);
  }

  constructor(private httpClient: HttpClient) {} 

}