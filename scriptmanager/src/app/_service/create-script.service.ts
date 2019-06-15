import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment'

@Injectable({
  providedIn: 'root'
})
export class CreateScriptService {
  public env =  environment;
  public apiUrl = this.env['apiUrlScript']

  public postScript(tid,data) {
    const _url = `${this.apiUrl}/tutorial/${tid}/scripts/`
    var ls = this.httpClient.post(
      _url,
      data
    );
    return ls;
  }

  public patchScript(tid,data) {
    console.log(data);
    const _url = `${this.apiUrl}/tutorial/${tid}/scripts/`
    var ls = this.httpClient.patch(
      _url,
      data
    );
    return ls;
  }

  public deleteScript(tid,srcipt_pk) {
    const _url = `${this.apiUrl}/tutorial/${tid}/scripts/${srcipt_pk}/`
    var ls = this.httpClient.delete(
      _url
    );
    return ls;
  }

  public getScript(tid){
    const _url = `${this.apiUrl}/tutorial/${tid}/scripts/`
    return this.httpClient.get(_url);
  }  

  constructor(private httpClient: HttpClient) { }
}
