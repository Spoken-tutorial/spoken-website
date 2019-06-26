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

  public postFile(tid, file) {
    this.testData.append('docs', file);
    const _url = `${this.apiUrl}/tutorial/${tid}/scripts/docs/`
    return this.http.post(_url, this.testData);
  }

  constructor(public http: HttpClient) { }
  
}
