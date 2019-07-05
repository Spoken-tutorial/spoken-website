import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})

export class UploadFileService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']
  public testData: FormData = new FormData();

  public postFile(tid, lid, file) {
    this.testData.append('docs', file);
    this.testData.append('type','file');
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    return this.http.post(_url,this.testData)
  }

  constructor(public http: HttpClient) { }
  
}
