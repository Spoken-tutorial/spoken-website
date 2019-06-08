import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class CreateScriptService {

  public postScript(tid,data) {
    console.log("post")
    var ls = this.http.post(
      'http://localhost:8000/scripts/api/tutorial/'+tid+'/script/create/',
       data
    );
    console.log(ls)
    return ls;
  }
  constructor(private http: HttpClient) { }
}
